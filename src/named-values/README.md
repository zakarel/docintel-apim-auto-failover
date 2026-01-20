# APIM Named Values Configuration

This directory contains named value (formerly called "properties") configurations for Azure API Management.

## Files

### `doc-active-backend.json`
Controls which backend is currently active for Document Intelligence requests:
- **Value**: `doc-west` (default) or `doc-north`
- **Purpose**: Dynamic backend selection without policy changes
- **Usage**: Referenced in policies as `{{doc-active-backend}}`

## Backend Switching

To switch between regions, update the named value:

```bash
# Switch to North Europe backend
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ApiManagement/service/{serviceName}/namedValues/doc-active-backend?api-version=2023-05-01-preview" \
  --body '{"properties": {"value": "doc-north", "displayName": "doc-active-backend"}}'

# Switch to West US 2 backend
az rest --method PUT \
  --url "https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroup}/providers/Microsoft.ApiManagement/service/{serviceName}/namedValues/doc-active-backend?api-version=2023-05-01-preview" \
  --body '{"properties": {"value": "doc-west", "displayName": "doc-active-backend"}}'
```

## Automatic Switching

The enhanced policies in `/src/policies/` automatically switch backends when:
- GET request duration exceeds 20 seconds
- Original backend becomes unavailable
- This provides resilience without manual intervention