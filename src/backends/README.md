# APIM Backends Configuration

This directory contains backend service definitions for Azure API Management.

## Files

### `doc-north-backend.json` 
Backend configuration for Document Intelligence in North Europe region:
- Service URL and authentication
- Connection settings and timeout configuration
- Health check and retry policies

### `doc-west-backend.json`
Backend configuration for Document Intelligence in West US 2 region:
- Service URL and authentication  
- Connection settings and timeout configuration
- Health check and retry policies

## Backend Selection

The active backend is controlled by the named value `doc-active-backend` which can be:
- `doc-north` - Routes to North Europe backend
- `doc-west` - Routes to West US 2 backend (default)

## Deployment

Deploy backends using Azure CLI:

```bash
# Deploy North Europe backend
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ApiManagement/service/{serviceName}/backends/doc-north?api-version=2023-05-01-preview" \
  --body @doc-north-backend.json

# Deploy West US 2 backend  
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ApiManagement/service/{serviceName}/backends/doc-west?api-version=2023-05-01-preview" \
  --body @doc-west-backend.json
```