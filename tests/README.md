# Tests Directory

This directory contains test suites for the Document Intelligence APIM solution.

## Structure

### `integration/`
Live test suite for APIM routing:
- `test_automatic_backend_switching.py` - Long-running APIM routing soak via the SDK

### `test-data/`
Test documents used by the test suites:
- Sample PDF documents for invoice analysis
- Various document types for testing different scenarios

## Running Tests

### Integration Tests
```bash
# Run from project root
# Automatic backend switching soak test (override document via --sample if needed)
python tests/integration/test_automatic_backend_switching.py --sample tests/test-data/small.pdf
```

### Environment Setup
Ensure your `.env` file is configured with:
```
AZURE_APIM_ENDPOINT="https://your-apim-service.azure-api.net/"
AZURE_APIM_KEY="your-apim-subscription-key"
docIntelWestEndpoint="https://your-west-formrecognizer.cognitiveservices.azure.com/"
docIntelNorthEndpoint="https://your-north-formrecognizer.cognitiveservices.azure.com/"
```

`test_automatic_backend_switching.py` also supports the `--sample` CLI argument (or the
`BACKEND_SWITCH_TEST_SAMPLE` environment variable) to point at a specific document file:

```
python tests/integration/test_automatic_backend_switching.py --sample ./tests/test-data/large.pdf
```

Optional knobs:

```
BACKEND_SWITCH_TEST_SAMPLE=tests/test-data/small.pdf
BACKEND_SWITCH_TEST_POLL_INTERVAL=1
BACKEND_SWITCH_TEST_DELAY=2
```

## Test Features

`test_automatic_backend_switching.py` validates:
- ✅ Document analysis through APIM via the Azure SDK
- ✅ Backend identification and automatic switching diagnostics headers
- ✅ Continuation token capture plus operation URL tracing
- ✅ Long-running stability across repeated runs