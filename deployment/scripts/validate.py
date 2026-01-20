#!/usr/bin/env python3
"""
Configuration Validation Script
Validates Terraform configuration, Azure connectivity, and resource prerequisites
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Color codes
class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    OKCYAN = '\033[96m'


def print_check(message: str, passed: bool):
    """Print validation check result"""
    symbol = f"{Colors.OKGREEN}✓{Colors.ENDC}" if passed else f"{Colors.FAIL}✗{Colors.ENDC}"
    print(f"{symbol} {message}")
    return passed


def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.OKCYAN}{'─'*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{title}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.OKCYAN}{'─'*80}{Colors.ENDC}")


def run_command(cmd: List[str], check: bool = False) -> Tuple[bool, str, str]:
    """Run command and return success status, stdout, stderr"""
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=check,
            timeout=30
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return False, "", "Command timed out"
    except Exception as e:
        return False, "", str(e)


def validate_tools() -> bool:
    """Validate required tools are installed"""
    print_section("Tool Prerequisites")
    
    all_passed = True
    
    # Terraform
    success, stdout, _ = run_command(["terraform", "version"])
    if success and stdout:
        version = stdout.split('\n')[0].replace("Terraform v", "")
        all_passed &= print_check(f"Terraform installed (version {version})", True)
    else:
        all_passed &= print_check("Terraform installed", False)
    
    # Azure CLI
    success, stdout, _ = run_command(["az", "version"])
    if success:
        all_passed &= print_check("Azure CLI installed", True)
    else:
        all_passed &= print_check("Azure CLI installed", False)
    
    # Python version
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    all_passed &= print_check(f"Python installed (version {py_version})", True)
    
    return all_passed


def validate_azure_auth() -> Tuple[bool, Optional[str]]:
    """Validate Azure authentication"""
    print_section("Azure Authentication")
    
    success, stdout, stderr = run_command(["az", "account", "show"])
    if not success:
        print_check("Azure CLI authenticated", False)
        print(f"{Colors.WARNING}  Run: az login{Colors.ENDC}")
        return False, None
    
    try:
        account = json.loads(stdout)
        subscription_id = account.get("id")
        subscription_name = account.get("name")
        user = account.get("user", {}).get("name", "Unknown")
        
        print_check(f"Authenticated as: {user}", True)
        print_check(f"Subscription: {subscription_name}", True)
        
        return True, subscription_id
    except json.JSONDecodeError:
        print_check("Parse Azure account info", False)
        return False, None


def validate_terraform_config(terraform_dir: Path) -> bool:
    """Validate Terraform configuration"""
    print_section("Terraform Configuration")
    
    if not terraform_dir.exists():
        return print_check(f"Terraform directory exists: {terraform_dir}", False)
    
    print_check(f"Terraform directory exists: {terraform_dir}", True)
    
    # Check for required files
    required_files = ["main.tf", "variables.tf", "outputs.tf"]
    all_passed = True
    
    for file in required_files:
        file_path = terraform_dir / file
        all_passed &= print_check(f"  {file} exists", file_path.exists())
    
    # Check modules
    modules_dir = terraform_dir / "modules"
    required_modules = ["backend-pools", "named-values", "api", "policies"]
    
    for module in required_modules:
        module_path = modules_dir / module / "main.tf"
        all_passed &= print_check(f"  Module {module} exists", module_path.exists())
    
    # Validate with terraform validate (if initialized)
    if (terraform_dir / ".terraform").exists():
        success, _, stderr = run_command(["terraform", "validate"], check=False)
        all_passed &= print_check("Terraform configuration valid", success)
        if not success and stderr:
            print(f"{Colors.WARNING}  {stderr}{Colors.ENDC}")
    else:
        print_check("Terraform initialized (skipping validate)", False)
        print(f"{Colors.WARNING}  Run: cd terraform && terraform init{Colors.ENDC}")
    
    return all_passed


def validate_environment_config(tfvars_file: Path) -> bool:
    """Validate environment configuration"""
    print_section(f"Environment Configuration: {tfvars_file.name}")
    
    if not tfvars_file.exists():
        print_check(f"Configuration file exists: {tfvars_file}", False)
        print(f"{Colors.WARNING}  Copy from template: cp {tfvars_file.parent}/dev.tfvars {tfvars_file}{Colors.ENDC}")
        return False
    
    print_check(f"Configuration file exists: {tfvars_file}", True)
    
    # Read and check required variables
    required_vars = ["subscription_id", "resource_group_name", "apim_service_name"]
    all_passed = True
    
    try:
        content = tfvars_file.read_text()
        for var in required_vars:
            if f'{var} = ' in content or f'{var}=' in content:
                # Check if value is placeholder
                if "your-" in content.lower() or "xxxxx" in content.lower():
                    all_passed &= print_check(f"  {var} configured (has placeholder)", False)
                else:
                    all_passed &= print_check(f"  {var} configured", True)
            else:
                all_passed &= print_check(f"  {var} configured", False)
    except Exception as e:
        print_check(f"Read configuration file", False)
        print(f"{Colors.FAIL}  Error: {e}{Colors.ENDC}")
        return False
    
    return all_passed


def validate_azure_resources(subscription_id: str, resource_group: str, apim_name: str) -> bool:
    """Validate Azure resources exist"""
    print_section("Azure Resources")
    
    all_passed = True
    
    # Check APIM service
    cmd = [
        "az", "apim", "show",
        "--name", apim_name,
        "--resource-group", resource_group,
        "--subscription", subscription_id
    ]
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print_check(f"APIM service '{apim_name}' exists", True)
        try:
            apim_info = json.loads(stdout)
            gateway_url = apim_info.get("gatewayUrl", "N/A")
            print(f"  {Colors.OKCYAN}Gateway URL: {gateway_url}{Colors.ENDC}")
        except:
            pass
    else:
        all_passed &= print_check(f"APIM service '{apim_name}' exists", False)
    
    return all_passed


def main():
    parser = argparse.ArgumentParser(description="Validate APIM Document Intelligence deployment configuration")
    parser.add_argument(
        "-e", "--environment",
        choices=["dev", "prod"],
        default="dev",
        help="Environment to validate (default: dev)"
    )
    parser.add_argument(
        "--tfvars",
        type=Path,
        help="Path to custom .tfvars file"
    )
    parser.add_argument(
        "--skip-azure-resources",
        action="store_true",
        help="Skip Azure resource validation"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent.parent
    terraform_dir = script_dir / "terraform"
    
    if args.tfvars:
        tfvars_file = args.tfvars
    else:
        tfvars_file = terraform_dir / "environments" / f"{args.environment}.tfvars"
    
    print(f"\n{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}APIM Document Intelligence - Configuration Validation{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*80}{Colors.ENDC}")
    
    all_checks_passed = True
    
    # Run validations
    all_checks_passed &= validate_tools()
    
    auth_passed, subscription_id = validate_azure_auth()
    all_checks_passed &= auth_passed
    
    all_checks_passed &= validate_terraform_config(terraform_dir)
    all_checks_passed &= validate_environment_config(tfvars_file)
    
    # Validate Azure resources if authenticated
    if auth_passed and not args.skip_azure_resources:
        try:
            content = tfvars_file.read_text()
            # Simple parsing - extract values
            import re
            
            rg_match = re.search(r'resource_group_name\s*=\s*"([^"]+)"', content)
            apim_match = re.search(r'apim_service_name\s*=\s*"([^"]+)"', content)
            
            if rg_match and apim_match:
                resource_group = rg_match.group(1)
                apim_name = apim_match.group(1)
                
                if not ("your-" in resource_group.lower() or "your-" in apim_name.lower()):
                    all_checks_passed &= validate_azure_resources(subscription_id, resource_group, apim_name)
        except:
            pass
    
    # Summary
    print_section("Validation Summary")
    if all_checks_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}✓ All validation checks passed!{Colors.ENDC}")
        print(f"\n{Colors.OKCYAN}Ready to deploy. Run:{Colors.ENDC}")
        print(f"  python deployment/scripts/deploy.py -e {args.environment}")
        sys.exit(0)
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}✗ Some validation checks failed{Colors.ENDC}")
        print(f"\n{Colors.WARNING}Fix the issues above before deploying{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
