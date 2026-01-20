# Backend Pools Module for Document Intelligence
# Creates load-balanced backend pools with priority-based routing

terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
  }
}

# West Region Backend Pool
resource "azurerm_api_management_backend" "west_pool" {
  name                = "doc-west-pool"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  protocol            = "http"
  url                 = "https://placeholder.cognitiveservices.azure.com"
  description         = "Document Intelligence West Region Pool"
  
  # Backend pool configuration with priority-based load balancing
  pool {
    dynamic "backend" {
      for_each = var.west_backends
      content {
        name     = "west-backend-${backend.value.priority}"
        priority = backend.value.priority
        weight   = 1
        address  = backend.value.url
        port     = 443
      }
    }
  }

  # Circuit breaker configuration
  circuit_breaker {
    rules {
      failure_condition {
        count         = 3
        error_reasons = ["ServerError"]
        interval      = "PT30S"
        status_code_ranges = [
          "500-599"
        ]
      }
      name         = "server-errors"
      trip_duration = "PT1M"
    }
    
    rules {
      failure_condition {
        count         = 5
        error_reasons = ["RequestTimeout"]
        interval      = "PT30S"
        status_code_ranges = [
          "408",
          "504"
        ]
      }
      name         = "timeouts"
      trip_duration = "PT1M"
    }
    
    rules {
      failure_condition {
        count         = 10
        error_reasons = ["TooManyRequests"]
        interval      = "PT1M"
        status_code_ranges = [
          "429"
        ]
      }
      name         = "rate-limiting"
      trip_duration = "PT2M"
    }
  }

  # Retry policy for transient failures
  retry {
    count    = 3
    interval = 1
    
    on {
      error_type = ["ServerError", "TooManyRequests"]
      status_code_ranges = [
        "408",
        "429", 
        "500-599"
      ]
    }
  }
}

# North Region Backend Pool
resource "azurerm_api_management_backend" "north_pool" {
  name                = "doc-north-pool"
  resource_group_name = var.resource_group_name
  api_management_name = var.apim_name
  protocol            = "http"
  url                 = "https://placeholder.cognitiveservices.azure.com"
  description         = "Document Intelligence North Region Pool"
  
  # Backend pool configuration with priority-based load balancing
  pool {
    dynamic "backend" {
      for_each = var.north_backends
      content {
        name     = "north-backend-${backend.value.priority}"
        priority = backend.value.priority
        weight   = 1
        address  = backend.value.url
        port     = 443
      }
    }
  }

  # Circuit breaker configuration (same as west)
  circuit_breaker {
    rules {
      failure_condition {
        count         = 3
        error_reasons = ["ServerError"]
        interval      = "PT30S"
        status_code_ranges = [
          "500-599"
        ]
      }
      name         = "server-errors"
      trip_duration = "PT1M"
    }
    
    rules {
      failure_condition {
        count         = 5
        error_reasons = ["RequestTimeout"]
        interval      = "PT30S"
        status_code_ranges = [
          "408",
          "504"
        ]
      }
      name         = "timeouts"
      trip_duration = "PT1M"
    }
    
    rules {
      failure_condition {
        count         = 10
        error_reasons = ["TooManyRequests"]
        interval      = "PT1M"
        status_code_ranges = [
          "429"
        ]
      }
      name         = "rate-limiting"
      trip_duration = "PT2M"
    }
  }

  # Retry policy for transient failures
  retry {
    count    = 3
    interval = 1
    
    on {
      error_type = ["ServerError", "TooManyRequests"]
      status_code_ranges = [
        "408",
        "429",
        "500-599"
      ]
    }
  }
}
