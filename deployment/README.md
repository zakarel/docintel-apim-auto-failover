# Deployment Scripts

Automated deployment tooling for the APIM Document Intelligence solution.

## Scripts

### `deploy.py`
Orchestrates Terraform deployment with validation and error handling.

**Usage:**
```bash
# Development deployment
python deployment/scripts/deploy.py -e dev

# Production deployment
python deployment/scripts/deploy.py -e prod

# Plan only (no apply)
python deployment/scripts/deploy.py -e dev --plan-only

# Custom tfvars file
python deployment/scripts/deploy.py --tfvars path/to/custom.tfvars

# Auto-approve (CI/CD)
python deployment/scripts/deploy.py -e prod --auto-approve
```

**Options:**
- `-e, --environment`: Deployment environment (`dev` or `prod`, default: `dev`)
- `--tfvars`: Path to custom .tfvars file
- `--skip-validation`: Skip Terraform validation
- `--plan-only`: Only run plan without applying
- `--auto-approve`: Auto-approve Terraform apply (use with caution)
- `--skip-prerequisites`: Skip prerequisite checks

### `validate.py`
Validates configuration, Azure connectivity, and resource prerequisites.

**Usage:**
```bash
# Validate development configuration
python deployment/scripts/validate.py -e dev

# Validate production configuration
python deployment/scripts/validate.py -e prod

# Validate custom tfvars
python deployment/scripts/validate.py --tfvars path/to/custom.tfvars

# Skip Azure resource checks
python deployment/scripts/validate.py -e dev --skip-azure-resources
```

**Options:**
- `-e, --environment`: Environment to validate (`dev` or `prod`, default: `dev`)
- `--tfvars`: Path to custom .tfvars file
- `--skip-azure-resources`: Skip Azure resource validation

## Validation Checks

The validation script checks:

1. **Tool Prerequisites**
   - Terraform installation and version
   - Azure CLI installation
   - Python version

2. **Azure Authentication**
   - Azure CLI login status
   - Active subscription details

3. **Terraform Configuration**
   - Required Terraform files exist
   - Module structure is correct
   - Configuration is valid (if initialized)

4. **Environment Configuration**
   - .tfvars file exists
   - Required variables are set
   - No placeholder values remain

5. **Azure Resources** (optional)
   - APIM service exists
   - Resource group is accessible

## Deployment Workflow

### First-Time Setup

1. **Validate prerequisites:**
   ```bash
   python deployment/scripts/validate.py -e dev
   ```

2. **Configure environment:**
   ```bash
   cp terraform/environments/dev.tfvars terraform/environments/dev.auto.tfvars
   # Edit dev.auto.tfvars with your values
   ```

3. **Validate configuration:**
   ```bash
   python deployment/scripts/validate.py -e dev
   ```

4. **Deploy:**
   ```bash
   python deployment/scripts/deploy.py -e dev
   ```

### Updates

1. **Plan changes:**
   ```bash
   python deployment/scripts/deploy.py -e dev --plan-only
   ```

2. **Apply changes:**
   ```bash
   python deployment/scripts/deploy.py -e dev
   ```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy APIM

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
      
      - name: Azure Login
        uses: azure/login@v1
        with:
          creds: ${{ secrets.AZURE_CREDENTIALS }}
      
      - name: Validate Configuration
        run: python deployment/scripts/validate.py -e prod
      
      - name: Deploy
        run: python deployment/scripts/deploy.py -e prod --auto-approve
```

### Azure DevOps Pipeline Example

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

steps:
  - task: TerraformInstaller@0
    inputs:
      terraformVersion: 'latest'
  
  - task: AzureCLI@2
    displayName: 'Validate and Deploy'
    inputs:
      azureSubscription: 'Azure-Subscription'
      scriptType: 'bash'
      scriptLocation: 'inlineScript'
      inlineScript: |
        python deployment/scripts/validate.py -e prod
        python deployment/scripts/deploy.py -e prod --auto-approve
```

## Error Handling

The deployment scripts handle common errors:

- **Missing prerequisites**: Provides installation instructions
- **Azure authentication**: Prompts for `az login`
- **Invalid configuration**: Shows specific validation failures
- **Terraform errors**: Displays detailed error messages
- **User cancellation**: Graceful exit with cleanup

## Logging

Deployment output includes:
- ✓ Success indicators (green)
- ✗ Failure indicators (red)
- ⚠ Warning indicators (yellow)
- ℹ Information indicators (cyan)

## Troubleshooting

### "Terraform not found"
```bash
# Install Terraform
# macOS
brew install terraform

# Windows
choco install terraform

# Linux
wget https://releases.hashicorp.com/terraform/1.5.0/terraform_1.5.0_linux_amd64.zip
unzip terraform_1.5.0_linux_amd64.zip
sudo mv terraform /usr/local/bin/
```

### "Not authenticated with Azure"
```bash
az login
az account set --subscription "your-subscription-id"
```

### "Configuration validation failed"
Check the specific error messages and ensure:
- All required variables are set in .tfvars
- No placeholder values remain
- Azure resources exist and are accessible

### "Terraform state locked"
```bash
cd terraform
terraform force-unlock <lock-id>
```

## Best Practices

1. **Always validate before deploying**
   ```bash
   python deployment/scripts/validate.py -e <env>
   ```

2. **Review plans before applying**
   ```bash
   python deployment/scripts/deploy.py -e <env> --plan-only
   ```

3. **Use separate environments**
   - Development: Quick iterations, testing
   - Production: Stable, reviewed changes

4. **Version control your changes**
   - Never commit `.auto.tfvars` files
   - Use environment-specific branches for production

5. **Test in development first**
   - Deploy to dev environment
   - Validate functionality
   - Then promote to production
