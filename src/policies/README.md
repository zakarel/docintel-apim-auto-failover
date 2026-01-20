# APIM Policies

This directory contains the working Azure API Management policies for the Document Intelligence service.

## Policy Files

### `analyze-operation-policy.xml`
- **Scope**: Applied to the analyze operation (POST /documentintelligence/documentModels/{modelId}:analyze)
- **Purpose**: 
  - Captures request start time for duration tracking
  - Modifies Operation-Location header to point back to APIM
  - Adds requestTime and backendId query parameters for enhanced routing

### `api-level-policy.xml` 
- **Scope**: Applied to the entire Document Intelligence API
- **Purpose**:
  - Manages backend selection based on named values
  - Implements automatic backend switching when request duration exceeds 20 seconds
  - Adds response headers for monitoring (X-Backend-Used, X-Request-Duration)
  - Handles both POST (analyze) and GET (result polling) requests

### `get-result-policy.xml`
- **Scope**: Applied to the get result operation (GET /documentintelligence/documentModels/{modelId}/analyzeResults/{resultId})
- **Purpose**:
  - Handles result polling requests
  - Routes to appropriate backend based on query parameters
  - Maintains consistency with the backend used during analysis

## Policy Features

### Enhanced Timing
- Captures request timestamps for duration calculation
- Automatically switches backends if polling exceeds 20-second threshold
- Provides timing information in response headers

### Backend Management  
- Dynamic backend selection based on `{{doc-active-backend}}` named value
- Automatic failover between `doc-north` and `doc-west` backends
- Query parameter routing for consistent backend usage during polling

### Header Management
- Strips client subscription keys to prevent leakage
- Adds monitoring headers for observability
- Modifies Operation-Location for proper APIM routing

### Deployment commands
```bash
# Deploy API-level policy
az apim api policy create \
  --resource-group <resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --xml-path api-level-policy.xml

# Deploy operation-level policy for analyze
az apim api operation policy create \
  --resource-group <resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --operation-id <analyze-operation-id> \
  --xml-path analyze-operation-policy.xml

# Deploy operation-level policy for get result
az apim api operation policy create \
  --resource-group <resource-group> \
  --service-name <apim-service-name> \
  --api-id <api-id> \
  --operation-id <get-result-operation-id> \
  --xml-path get-result-policy.xml
```