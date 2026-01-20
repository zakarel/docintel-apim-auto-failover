#!/usr/bin/env python3
"""
Azure APIM Document Intelligence Solution - Deployment Script
Orchestrates Terraform deployment with validation and error handling
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_header(message: str):
    """Print formatted header message"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message.center(80)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message"""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message"""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}", file=sys.stderr)


def print_warning(message: str):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def run_command(cmd: List[str], cwd: Optional[Path] = None, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command and return result"""
    print_info(f"Running: {' '.join(cmd)}")
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            check=check,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed with exit code {e.returncode}")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr, file=sys.stderr)
        raise


def check_prerequisites():
    """Check if required tools are installed"""
    print_header("Checking Prerequisites")
    
    prerequisites = {
        "terraform": ["terraform", "version"],
        "azure-cli": ["az", "version"],
    }
    
    missing = []
    
    for tool, cmd in prerequisites.items():
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            version = result.stdout.split('\n')[0] if result.stdout else "unknown"
            print_success(f"{tool}: {version}")
        except (subprocess.CalledProcessError, FileNotFoundError):
            print_error(f"{tool} not found")
            missing.append(tool)
    
    if missing:
        print_error(f"Missing prerequisites: {', '.join(missing)}")
        print_info("Install missing tools:")
        print_info("  - Terraform: https://www.terraform.io/downloads")
        print_info("  - Azure CLI: https://docs.microsoft.com/cli/azure/install-azure-cli")
        sys.exit(1)
    
    print_success("All prerequisites met")


def check_azure_login():
    """Check if user is logged into Azure CLI"""
    print_header("Checking Azure Authentication")
    
    try:
        result = subprocess.run(
            ["az", "account", "show"],
            capture_output=True,
            text=True,
            check=True
        )
        account_info = json.loads(result.stdout)
        print_success(f"Logged in as: {account_info.get('user', {}).get('name', 'Unknown')}")
        print_success(f"Subscription: {account_info.get('name', 'Unknown')} ({account_info.get('id', 'Unknown')})")
        return True
    except (subprocess.CalledProcessError, json.JSONDecodeError):
        print_error("Not logged into Azure CLI")
        print_info("Run: az login")
        return False


def validate_tfvars(tfvars_file: Path):
    """Validate terraform variables file exists"""
    if not tfvars_file.exists():
        print_error(f"Terraform variables file not found: {tfvars_file}")
        print_info("Create it by copying from template:")
        print_info(f"  cp {tfvars_file.parent / 'dev.tfvars'} {tfvars_file}")
        sys.exit(1)
    print_success(f"Found variables file: {tfvars_file}")


def terraform_init(terraform_dir: Path):
    """Initialize Terraform"""
    print_header("Initializing Terraform")
    run_command(["terraform", "init", "-upgrade"], cwd=terraform_dir)
    print_success("Terraform initialized")


def terraform_validate(terraform_dir: Path):
    """Validate Terraform configuration"""
    print_header("Validating Terraform Configuration")
    run_command(["terraform", "validate"], cwd=terraform_dir)
    print_success("Terraform configuration valid")


def terraform_plan(terraform_dir: Path, tfvars_file: Path, out_file: Optional[Path] = None):
    """Run Terraform plan"""
    print_header("Planning Terraform Deployment")
    
    cmd = ["terraform", "plan", f"-var-file={tfvars_file}"]
    if out_file:
        cmd.append(f"-out={out_file}")
    
    run_command(cmd, cwd=terraform_dir)
    print_success("Terraform plan completed")


def terraform_apply(terraform_dir: Path, plan_file: Optional[Path] = None, tfvars_file: Optional[Path] = None, auto_approve: bool = False):
    """Apply Terraform configuration"""
    print_header("Applying Terraform Configuration")
    
    if not auto_approve:
        print_warning("This will create/modify Azure resources")
        response = input("Do you want to continue? (yes/no): ").strip().lower()
        if response != "yes":
            print_info("Deployment cancelled")
            sys.exit(0)
    
    cmd = ["terraform", "apply"]
    if plan_file:
        cmd.append(str(plan_file))
    elif tfvars_file:
        cmd.extend([f"-var-file={tfvars_file}"])
        if auto_approve:
            cmd.append("-auto-approve")
    
    run_command(cmd, cwd=terraform_dir)
    print_success("Terraform apply completed")


def terraform_output(terraform_dir: Path):
    """Display Terraform outputs"""
    print_header("Terraform Outputs")
    result = run_command(["terraform", "output", "-json"], cwd=terraform_dir)
    
    try:
        outputs = json.loads(result.stdout)
        for key, value in outputs.items():
            print(f"  {Colors.OKBLUE}{key}{Colors.ENDC}: {value.get('value', 'N/A')}")
    except json.JSONDecodeError:
        print_warning("Could not parse Terraform outputs")


def main():
    parser = argparse.ArgumentParser(
        description="Deploy APIM Document Intelligence Solution with Terraform"
    )
    parser.add_argument(
        "-e", "--environment",
        choices=["dev", "prod"],
        default="dev",
        help="Deployment environment (default: dev)"
    )
    parser.add_argument(
        "--tfvars",
        type=Path,
        help="Path to custom .tfvars file"
    )
    parser.add_argument(
        "--skip-validation",
        action="store_true",
        help="Skip validation checks"
    )
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Only run plan without applying"
    )
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Auto-approve Terraform apply (use with caution)"
    )
    parser.add_argument(
        "--skip-prerequisites",
        action="store_true",
        help="Skip prerequisite checks"
    )
    
    args = parser.parse_args()
    
    # Determine paths
    script_dir = Path(__file__).parent.parent
    terraform_dir = script_dir / "terraform"
    
    if args.tfvars:
        tfvars_file = args.tfvars
    else:
        tfvars_file = terraform_dir / "environments" / f"{args.environment}.tfvars"
    
    plan_file = terraform_dir / f"{args.environment}.tfplan"
    
    print_header(f"APIM Document Intelligence Solution Deployment - {args.environment.upper()}")
    
    try:
        # Prerequisites
        if not args.skip_prerequisites:
            check_prerequisites()
            if not check_azure_login():
                sys.exit(1)
        
        # Validate tfvars file
        validate_tfvars(tfvars_file)
        
        # Terraform workflow
        terraform_init(terraform_dir)
        
        if not args.skip_validation:
            terraform_validate(terraform_dir)
        
        terraform_plan(terraform_dir, tfvars_file, plan_file if not args.plan_only else None)
        
        if args.plan_only:
            print_info("Plan-only mode: Skipping apply")
        else:
            terraform_apply(terraform_dir, plan_file if not args.auto_approve else None, tfvars_file, args.auto_approve)
            terraform_output(terraform_dir)
            
            print_header("Deployment Complete")
            print_success("APIM Document Intelligence solution deployed successfully!")
            print_info(f"Review outputs above for connection details")
            
            # Cleanup plan file
            if plan_file.exists():
                plan_file.unlink()
    
    except subprocess.CalledProcessError as e:
        print_header("Deployment Failed")
        print_error(f"Deployment failed with exit code {e.returncode}")
        sys.exit(1)
    except KeyboardInterrupt:
        print_warning("\nDeployment cancelled by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
