# APIM APIs Configuration

This directory contains API definitions for Azure API Management.

## Files

### `document-intelligence-api.json`
Complete API definition for the Azure Document Intelligence service including:
- API metadata and versioning
- Operation definitions (analyze, analyzeResults)
- Path templates and parameter mappings
- Authentication requirements

## Usage

Deploy using the Azure REST API or Azure CLI:

```bash
# Deploy API definition
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ApiManagement/service/{serviceName}/apis/document-intelligence?api-version=2023-05-01-preview" \
  --body @document-intelligence-api.json
```
