# Terraform Infrastructure

This directory contains the Terraform infrastructure-as-code for the APIM Document Intelligence solution.

## Structure

```
terraform/
├── main.tf                 # Main configuration with module orchestration
├── variables.tf            # Input variables
├── outputs.tf              # Output values
├── environments/           # Environment-specific configurations
│   ├── dev.tfvars         # Development environment
│   └── prod.tfvars        # Production environment
└── modules/               # Reusable Terraform modules
    ├── backend-pools/     # Backend pool configurations
    ├── named-values/      # APIM named values
    ├── api/              # API definitions
    └── policies/         # Policy deployments
```

## Prerequisites

- Terraform >= 1.5.0
- Azure CLI authenticated (`az login`)
- Existing Azure API Management service
- Document Intelligence resources in two regions

## Quick Start

### 1. Initialize Terraform

```bash
cd terraform
terraform init
```

### 2. Configure Environment

Copy and edit the appropriate `.tfvars` file:

```bash
# For development
cp environments/dev.tfvars environments/dev.auto.tfvars
# Edit dev.auto.tfvars with your values

# For production
cp environments/prod.tfvars environments/prod.auto.tfvars
# Edit prod.auto.tfvars with your values
```

### 3. Plan Deployment

```bash
# Development
terraform plan -var-file="environments/dev.tfvars"

# Production
terraform plan -var-file="environments/prod.tfvars"
```

### 4. Apply Configuration

```bash
# Development
terraform apply -var-file="environments/dev.tfvars"

# Production (requires approval)
terraform apply -var-file="environments/prod.tfvars"
```

## Configuration Options

### Backend Pools

Configure multiple Document Intelligence instances per region:

```hcl
west_backend_endpoints = [
  {
    url      = "https://di-west-1.cognitiveservices.azure.com"
    title    = "DI West Primary"
    priority = 1
  },
  {
    url      = "https://di-west-2.cognitiveservices.azure.com"
    title    = "DI West Secondary"
    priority = 2
  }
]
```

### Circuit Breaker Settings

```hcl
backend_switch_threshold  = 5.0   # Seconds before triggering failover
circuit_breaker_threshold = 50    # Error rate percentage (0-100)
circuit_breaker_timeout   = 30    # Evaluation window in seconds
```

## State Management

For production deployments, configure remote state in `main.tf`:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "tfstatexxxxx"
    container_name       = "tfstate"
    key                  = "apim-doc-intel.tfstate"
  }
}
```

## Outputs

After successful deployment:

```bash
# View all outputs
terraform output

# Get specific output
terraform output api_endpoint
```

## Best Practices

1. **Never commit `.auto.tfvars` files** - They contain sensitive configuration
2. **Use remote state for production** - Enable state locking and versioning
3. **Review plans carefully** - Always run `terraform plan` before `apply`
4. **Tag resources appropriately** - Use consistent tagging strategy
5. **Version control modules** - Pin module versions in production

## Troubleshooting

### Authentication Issues

```bash
# Login to Azure
az login

# Verify subscription
az account show

# Set specific subscription
az account set --subscription "your-subscription-id"
```

### State Lock Issues

If state is locked:

```bash
# Force unlock (use with caution)
terraform force-unlock <lock-id>
```

### Module Errors

```bash
# Reinitialize modules
terraform init -upgrade

# Validate configuration
terraform validate
```

## Useful Commands

```bash
# Format configuration
terraform fmt -recursive

# Validate configuration
terraform validate

# Show current state
terraform show

# List resources in state
terraform state list

# Import existing resource
terraform import <resource_type>.<resource_name> <resource_id>

# Destroy infrastructure (use with extreme caution)
terraform destroy -var-file="environments/dev.tfvars"
```
