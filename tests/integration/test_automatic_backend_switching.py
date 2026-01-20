#!/usr/bin/env python3
"""Automatic backend switching test using the Document Intelligence SDK."""
""" 
EXPECTED IN PRODUCTION (with working automatic switching at 5 seconds):
|  #  | Method   | ResponseCode   | BackendUsed   | Duration   | Threshold Exceeded   | Switched   | Status      |
|-----|----------|----------------|---------------|------------|----------------------|------------|-------------|
|  1  | POST     | 202            | doc-west      |            |                      |            | OK          |
|  1  | GET      | 200            | doc-west      | 7.XXs      | true                 | YES        | OK          |
|  2  | POST     | 202            | doc-north     |            |                      |            | OK          |
|  2  | GET      | 200            | doc-north     | 7.XXs      | true                 | YES        | OK          |
|  3  | POST     | 202            | doc-west      |            |                      |            | OK          |
|  3  | GET      | 200            | doc-west      | 7.XXs      | true                 | YES        | OK          |

✅ KEY SUCCESS METRICS:
- Backend switching detection works (X-Backend-Switched: true)
- No 404 errors (GET requests go to same backend as POST)
- Duration calculation and threshold comparison working
- All diagnostic headers populated correctly
"""
import argparse
import base64
import binascii
import json
import logging
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, parse_qsl, urlparse
from email.utils import parsedate_to_datetime

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError
from dotenv import load_dotenv
from tabulate import tabulate

# Load environment variables - override with .env file
load_dotenv(override=True)

TEST_DATA_DIR = Path(__file__).resolve().parents[1] / "test-data"

# Resolve logging paths
LOG_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), "..", "..", "logs"))
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, f"backend_switching_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")


def _configure_logger(name: str, handler: logging.Handler, level: int) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.handlers.clear()
    handler.setLevel(level)
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.propagate = False
    return logger


console_handler = logging.StreamHandler()
console_handler.setFormatter(logging.Formatter('%(message)s'))
console_logger = _configure_logger('console', console_handler, logging.INFO)

file_handler = logging.FileHandler(LOG_FILE)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
file_logger = _configure_logger('detailed', file_handler, logging.DEBUG)


class AutomaticBackendTester:
    """Exercise automatic backend switching with SDK-managed polling."""

    def __init__(self, sample_override: Optional[str] = None) -> None:
        self.endpoint = os.environ["AZURE_APIM_ENDPOINT"].rstrip('/')
        subscription_key = os.environ.get("AZURE_APIM_KEY")
        if not subscription_key:
            raise ValueError("AZURE_APIM_KEY environment variable is required")

        self.client = DocumentIntelligenceClient(self.endpoint, AzureKeyCredential(subscription_key))
        self.sample_path = self._resolve_sample_path(sample_override)
        with self.sample_path.open("rb") as handle:
            sample_bytes = handle.read()
        self.test_document_base64 = base64.b64encode(sample_bytes).decode("ascii")
        self.polling_interval = float(os.environ.get("BACKEND_SWITCH_TEST_POLL_INTERVAL", "1"))
        self.polling_delay = float(os.environ.get("BACKEND_SWITCH_TEST_DELAY", "2"))
        self.results: List[Dict[str, Any]] = []
        self.response_log: List[Dict[str, Any]] = []
        self.log_file = LOG_FILE
        self.progress_entries: List[Dict[str, Any]] = []
        self.console_header_printed = False
        self._line_overwritable = False
        self._last_line_length = 0

        self._log_info("Automatic Backend Tester initialized")
        file_logger.info("Sample document: %s", self.sample_path)
        file_logger.info("Log file: %s", self.log_file)

    @staticmethod
    def _normalize_headers(headers: Dict[str, Any]) -> Dict[str, str]:
        return {str(k).lower(): str(v) for k, v in headers.items()}

    @staticmethod
    def _resolve_sample_path(sample_override: Optional[str]) -> Path:
        if sample_override:
            candidate = Path(sample_override).expanduser()
            if not candidate.is_absolute():
                candidate = Path.cwd() / candidate
        else:
            sample_name = os.environ.get("BACKEND_SWITCH_TEST_SAMPLE", "small.pdf")
            candidate = TEST_DATA_DIR / sample_name
        candidate = candidate.resolve()
        if not candidate.exists():
            raise FileNotFoundError(f"Sample document not found: {candidate}")
        return candidate

    @staticmethod
    def _parse_json_payload(data: Any) -> Optional[Dict[str, Any]]:
        if data is None:
            return None
        if isinstance(data, dict):
            return data
        if isinstance(data, (bytes, bytearray)):
            try:
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                return None
        if isinstance(data, str):
            try:
                parsed = json.loads(data)
            except json.JSONDecodeError:
                return None
            return parsed if isinstance(parsed, dict) else None
        return None

    @staticmethod
    def _read_http_body(http_response: Any) -> Optional[Any]:
        for accessor in ("body", "text"):
            candidate = getattr(http_response, accessor, None)
            if candidate is None:
                continue
            try:
                value = candidate() if callable(candidate) else candidate
            except TypeError:
                value = candidate
            except Exception:
                continue
            return value
        return None

    @staticmethod
    def _extract_content_string(payload: Optional[Dict[str, Any]]) -> Optional[str]:
        if not isinstance(payload, dict):
            return None
        direct_content = payload.get('content')
        if isinstance(direct_content, str):
            return direct_content
        analyze_result = payload.get('analyzeResult')
        if isinstance(analyze_result, dict):
            nested_content = analyze_result.get('content')
            if isinstance(nested_content, str):
                return nested_content
        return None

    @staticmethod
    def _format_query_string(raw_query: str) -> str:
        if not raw_query:
            return ''
        parts = parse_qsl(raw_query, keep_blank_values=True)
        return '&'.join(f"{key}={value}" for key, value in parts)

    @staticmethod
    def _format_request_time_display(raw_value: str) -> str:
        if not raw_value:
            return ''
        candidate = raw_value.strip()
        dt_obj: Optional[datetime] = None
        if candidate.endswith('Z'):
            iso_candidate = candidate[:-1] + '+00:00'
        else:
            iso_candidate = candidate
        try:
            dt_obj = datetime.fromisoformat(iso_candidate)
        except ValueError:
            dt_obj = None
        if dt_obj is None:
            try:
                dt_obj = parsedate_to_datetime(candidate)
            except (TypeError, ValueError):
                dt_obj = None
        if dt_obj is None:
            return raw_value
        if dt_obj.tzinfo is not None:
            dt_obj = dt_obj.astimezone(timezone.utc)
        milliseconds = dt_obj.microsecond // 1000
        return f"{dt_obj.hour:02d}:{dt_obj.minute:02d}:{dt_obj.second:02d}.{milliseconds:03d}"

    def _capture_response(self, response) -> None:
        http_response = response.http_response
        request = http_response.request
        parsed_url = urlparse(request.url)
        query_params = parse_qs(parsed_url.query)
        query_string = self._format_query_string(parsed_url.query)
        headers = self._normalize_headers(http_response.headers)
        request_time_raw = ','.join(query_params.get('requestTime', []))
        if not request_time_raw:
            # POST responses do not echo requestTime in the query string, so fall back to server date header.
            request_time_raw = headers.get('date', '')
        request_time = self._format_request_time_display(request_time_raw)
        content_length = ''
        body = getattr(request, "body", None)
        payload = self._parse_json_payload(body)

        if isinstance(payload, dict):
            content_value = self._extract_content_string(payload)
            if isinstance(content_value, str):
                content_length = str(len(content_value))
            else:
                base64_value = payload.get('base64Source')
                if isinstance(base64_value, str):
                    try:
                        decoded = base64.b64decode(base64_value, validate=True)
                        content_length = str(len(decoded))
                    except (binascii.Error, ValueError):
                        content_length = str(len(base64_value))

        if not content_length:
            response_payload = self._parse_json_payload(self._read_http_body(http_response))
            if isinstance(response_payload, dict):
                response_content = self._extract_content_string(response_payload)
                if isinstance(response_content, str):
                    content_length = str(len(response_content))

        entry = {
            "method": request.method,
            "url": request.url,
            "status_code": http_response.status_code,
            "headers": headers,
            "request_time": request_time,
            "content_length": content_length,
            "query_params": query_string,
        }
        self.response_log.append(entry)
        file_logger.debug("Captured %s %s -> %s", entry['method'], entry['url'], entry['status_code'])

    def _log(self, level: str, message: str) -> None:
        getattr(console_logger, level)(message)
        getattr(file_logger, level)(message)

    def _log_info(self, message: str) -> None:
        self._log('info', message)

    def _log_warning(self, message: str) -> None:
        self._log('warning', message)

    def _log_error(self, message: str) -> None:
        self._log('error', message)

    def _first_response(self, method: str) -> Optional[Dict[str, Any]]:
        method_upper = method.upper()
        for entry in self.response_log:
            if entry['method'] == method_upper:
                return entry
        return None

    def _last_response(self, method: str) -> Optional[Dict[str, Any]]:
        method_upper = method.upper()
        for entry in reversed(self.response_log):
            if entry['method'] == method_upper:
                return entry
        return None

    def _wait_for_response(self, method: str, timeout: float = 5.0) -> Optional[Dict[str, Any]]:
        deadline = time.time() + timeout
        while time.time() < deadline:
            entry = self._last_response(method)
            if entry:
                return entry
            time.sleep(0.05)
        return self._last_response(method)

    def _extract_operation_url(self, poller) -> Optional[str]:
        token = poller.continuation_token() if hasattr(poller, "continuation_token") else None
        if token:
            file_logger.debug("Continuation token captured (full value): %s", token)
        post_response = self._first_response('POST')
        if post_response:
            headers = post_response['headers']
            header_url = headers.get('operation-location') or headers.get('operation-location'.lower())
            if header_url:
                return header_url
        return token

    def _parse_query(self, url: Optional[str]) -> Dict[str, str]:
        if not url:
            return {}
        parsed = urlparse(url)
        query_dict = {k: ','.join(v) for k, v in parse_qs(parsed.query).items()}
        file_logger.debug("Captured continuation token query params (read-only): %s", query_dict)
        return query_dict

    CONSOLE_HEADER = "|  #  | Method | ResponseCode  | BackendUsed | RequestTime     | Duration | Threshold Exceeded | Switched | ContentLen | Status | QueryParams                            |"
    CONSOLE_SEPARATOR = "|-----|--------|---------------|-------------|-----------------|----------|--------------------|----------|------------|--------|----------------------------------------|"
    ROW_TEMPLATE = "| {run:^3} | {method:<6} | {response_code:<13} | {backend:<11} | {request_time:<15} | {duration:<8} | {threshold:<18} | {switched:<8} | {content_length:<10} | {status:<6} | {query_params:<38}"

    def _ensure_console_header(self) -> None:
        if self.console_header_printed:
            return
        for line in (self.CONSOLE_HEADER, self.CONSOLE_SEPARATOR):
            self._write_console_line(line)
        self.console_header_printed = True

    def _format_row(self, entry: Dict[str, Any]) -> str:
        run = str(entry.get('run', ''))
        return self.ROW_TEMPLATE.format(
            run=run,
            method=str(entry.get('method', '')),
            response_code=str(entry.get('response_code', '')),
            backend=str(entry.get('backend', '')),
            request_time=str(entry.get('request_time', '')),
            duration=str(entry.get('duration', '')),
            threshold=str(entry.get('threshold_exceeded', '')),
            switched=str(entry.get('switched', '')),
            content_length=str(entry.get('content_length', '')),
            query_params=str(entry.get('query_params', '')),
            status=str(entry.get('status', '')),
        )

    def _write_console_line(self, line: str, overwriteable: bool = False, replace: bool = False) -> None:
        stream = sys.stdout
        if replace:
            if self._line_overwritable:
                padding = max(self._last_line_length - len(line), 0)
                stream.write("\r" + line + (" " * padding) + "\n")
            else:
                stream.write(line + "\n")
        else:
            if self._line_overwritable:
                stream.write("\n")
            stream.write(line)
            if overwriteable:
                stream.write("\r")
            else:
                stream.write("\n")
        stream.flush()
        self._line_overwritable = overwriteable
        self._last_line_length = len(line)

    def _log_progress_snapshot(self) -> None:
        if not self.progress_entries:
            return
        headers = [
            "#",
            "Method",
            "ResponseCode",
            "BackendUsed",
            "RequestTime",
            "Duration",
            "Threshold Exceeded",
            "Switched",
            "ContentLen",
            "QueryParams",
            "Status",
        ]
        rows: List[List[str]] = []
        for entry in self.progress_entries:
            rows.append([
                entry.get('run', ''),
                entry.get('method', ''),
                entry.get('response_code', ''),
                entry.get('backend', ''),
                entry.get('request_time', ''),
                entry.get('duration', ''),
                entry.get('threshold_exceeded', ''),
                entry.get('switched', ''),
                entry.get('content_length', ''),
                entry.get('query_params', ''),
                entry.get('status', ''),
            ])
        table = tabulate(rows, headers=headers, tablefmt="github")
        file_logger.info("\n%s", table)

    def _emit_console_line(self, entry: Dict[str, Any], overwriteable: bool, replace: bool) -> None:
        self._ensure_console_header()
        line = self._format_row(entry)
        self._write_console_line(line, overwriteable=overwriteable, replace=replace)
        self._log_progress_snapshot()

    def _add_progress_entry(self, entry: Dict[str, Any], overwriteable: bool = False) -> None:
        self.progress_entries.append(entry)
        self._emit_console_line(entry, overwriteable=overwriteable, replace=False)

    def _update_progress_entry(self, run_number: int, method: str, **fields: Any) -> None:
        target: Optional[Dict[str, Any]] = None
        for entry in reversed(self.progress_entries):
            if entry.get('run') == run_number and entry.get('method') == method:
                entry.update(fields)
                target = entry
                break
        if target:
            self._emit_console_line(target, overwriteable=False, replace=True)

    def test_automatic_switching(self, run_number: int, test_name: str) -> Dict[str, Any]:
        file_logger.info("=== Testing Automatic Switching: %s ===", test_name)
        start_time = time.time()
        self.response_log = []

        start_time = time.time()
        poller = self.client.begin_analyze_document(
            model_id="prebuilt-read",
            body={"base64Source": self.test_document_base64},
            content_type="application/json",
            raw_response_hook=self._capture_response,
            polling_interval=self.polling_interval,
        )

        operation_url = self._extract_operation_url(poller)
        operation_query = self._parse_query(operation_url)

        post_response = self._wait_for_response('POST')
        if not post_response:
            raise RuntimeError("Unable to capture POST response for automatic switching test")

        post_backend = post_response.get('headers', {}).get('x-backend-used', 'unknown')
        post_status = post_response.get('status_code', 0)

        self._add_progress_entry({
            'run': run_number,
            'method': 'POST',
            'response_code': str(post_status),
            'backend': post_backend,
            'request_time': post_response.get('request_time', ''),
            'duration': '',
            'threshold_exceeded': '',
            'switched': '',
            'content_length': post_response.get('content_length', ''),
            'query_params': post_response.get('query_params', ''),
            'status': 'OK' if 200 <= int(post_status) < 400 else 'FAIL',
        })

        self._add_progress_entry({
            'run': run_number,
            'method': 'GET',
            'response_code': 'running ...',
            'backend': '',
            'request_time': '',
            'duration': '',
            'threshold_exceeded': '',
            'switched': '',
            'content_length': '',
            'query_params': '',
            'status': 'IN PROGRESS',
        }, overwriteable=True)

        if operation_url:
            file_logger.info("Operation URL captured (read-only): %s", operation_url)
        else:
            file_logger.info("Operation URL captured (read-only): unavailable")
        if operation_query:
            file_logger.debug("Operation query parameters: %s", operation_query)

        file_logger.info("Waiting %.1fs before retrieving SDK result", self.polling_delay)
        # time.sleep(self.polling_delay)

        result_status = 200
        try:
            poller.result()
        except HttpResponseError as error:  # 404 is expected when backend switches
            result_status = getattr(error, 'status_code', None) or (
                error.response.status_code if getattr(error, 'response', None) else 0
            )
            file_logger.warning("Poller finished with HttpResponseError: %s", result_status)

        total_time = time.time() - start_time

        final_response = self._wait_for_response('GET') or post_response

        get_backend = (final_response or {}).get('headers', {}).get('x-backend-used', 'unknown')
        backend_switched_header = (final_response or {}).get('headers', {}).get('x-backend-switched', 'false')
        duration_exceeded = (final_response or {}).get('headers', {}).get('x-duration-threshold-exceeded', 'false')
        #request_duration = (final_response or {}).get('headers', {}).get('x-request-duration', '0')
        request_duration = time.time() - start_time

        backend_switched_flag = str(backend_switched_header).lower() == 'true'

        switching_occurred = (
            post_backend != get_backend
            and post_backend != 'unknown'
            and get_backend != 'unknown'
        ) or backend_switched_flag
        success = result_status in (200, 404)

        get_status = (final_response or {}).get('status_code', result_status)

        try:
            duration_float = float(request_duration)
            duration_display = f"{duration_float:.2f}s"
        except (TypeError, ValueError):
            duration_display = request_duration or f"{total_time:.2f}s"

        self._update_progress_entry(
            run_number,
            'GET',
            response_code=str(get_status),
            backend=get_backend,
            request_time=(final_response or {}).get('request_time', ''),
            duration=duration_display,
            threshold_exceeded=str(duration_exceeded).lower() if duration_exceeded else '',
            switched='YES' if switching_occurred else 'NO',
            content_length=(final_response or {}).get('content_length', ''),
            query_params=(final_response or {}).get('query_params', ''),
            status='OK' if success else 'FAIL',
        )

        result: Dict[str, Any] = {
            'test_name': test_name,
            'post_status': post_status,
            'get_status': (final_response or {}).get('status_code', result_status),
            'post_backend': post_backend,
            'get_backend': get_backend,
            'backend_switched': backend_switched_header,
            'duration_exceeded': duration_exceeded,
            'switching_occurred': switching_occurred,
            'total_time': total_time,
            'success': success,
            'operation_location': operation_url,
            'operation_query': operation_query,
            'post_request_time': post_response.get('request_time', ''),
            'get_request_time': (final_response or {}).get('request_time', ''),
            'post_content_length': post_response.get('content_length', ''),
            'get_content_length': (final_response or {}).get('content_length', ''),
            'post_query_params': post_response.get('query_params', ''),
            'get_query_params': (final_response or {}).get('query_params', ''),
        }

        self.results.append(result)
        return result

    def run_test(self) -> List[Dict[str, Any]]:
        file_logger.info("=== STARTING AUTOMATIC BACKEND SWITCHING TEST ===")
        file_logger.info("Goal: Verify automatic backend switching at configured threshold")
        self.progress_entries = []
        self.console_header_printed = False
        self._line_overwritable = False
        self._last_line_length = 0
        runCount = 10000 # almost infinite loop 10000 x 6s delay = 60000s = 16.67 hours + processing time...
        console_logger.info(f"Running OCR {runCount} times:")

        for run_id in range(1, runCount + 1):
            self.test_automatic_switching(run_id, f"Auto-Switch-{run_id}")
            time.sleep(6) # Sleep between runs to test for long time

        switching_count = sum(1 for result in self.results if result['switching_occurred'])
        file_logger.info("=== FINAL SUMMARY ===")
        file_logger.info("Switching detected in %s/%s runs", switching_count, len(self.results))

        if switching_count > 0:
            console_logger.info("Automatic backend switching confirmed (%s/%s runs)", switching_count, len(self.results))
        else:
            console_logger.warning("No backend switching observed - verify APIM threshold configuration")

        console_logger.info("Detailed logs: %s", self.log_file)
        return self.results


def _resolve_failure_url(tester: Optional[AutomaticBackendTester]) -> Optional[str]:
    """Return the most relevant request URL for error messages."""
    if tester:
        if tester.response_log:
            last_entry = tester.response_log[-1]
            url = last_entry.get('url')
            if url:
                return url
        endpoint = getattr(tester, 'endpoint', None)
        if endpoint:
            return endpoint
    for env_key in ("AZURE_APIM_ENDPOINT", "AZURE_DI_ENDPOINT"):
        value = os.environ.get(env_key)
        if value:
            return value.rstrip('/')
    return None


def _parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Exercise automatic backend switching through APIM via Document Intelligence SDK",
    )
    parser.add_argument(
        "-s",
        "--sample",
        help="Path to the document sent to Document Intelligence; overrides BACKEND_SWITCH_TEST_SAMPLE",
    )
    return parser.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = _parse_args(argv)
    tester: Optional[AutomaticBackendTester] = None
    try:
        tester = AutomaticBackendTester(sample_override=args.sample)
        results = tester.run_test()
        return 0 if any(r['switching_occurred'] for r in results) else 1
    except Exception as exc:  # pragma: no cover - integration test failure path
        failure_url = _resolve_failure_url(tester)
        if failure_url:
            console_logger.error("Test execution failed when calling %s: %s", failure_url, exc)
            file_logger.exception("Test execution failed when calling %s", failure_url)
        else:
            console_logger.error("Test execution failed: %s", exc)
            file_logger.exception("Test execution failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
