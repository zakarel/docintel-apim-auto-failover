# Terraform Variables for APIM Document Intelligence Solution

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name where APIM is deployed"
  type        = string
}

variable "apim_service_name" {
  description = "Name of the existing APIM service"
  type        = string
}

variable "api_path" {
  description = "Base path for the Document Intelligence API"
  type        = string
  default     = "doc"
}

variable "active_backend" {
  description = "Active backend pool (doc-west-pool or doc-north-pool)"
  type        = string
  default     = "doc-west-pool"
  
  validation {
    condition     = contains(["doc-west-pool", "doc-north-pool"], var.active_backend)
    error_message = "Active backend must be either 'doc-west-pool' or 'doc-north-pool'."
  }
}

variable "backend_switch_threshold" {
  description = "Latency threshold in seconds for automatic backend switching"
  type        = number
  default     = 5.0
  
  validation {
    condition     = var.backend_switch_threshold > 0 && var.backend_switch_threshold <= 60
    error_message = "Backend switch threshold must be between 0 and 60 seconds."
  }
}

variable "circuit_breaker_threshold" {
  description = "Error rate percentage to trigger circuit breaker (0-100)"
  type        = number
  default     = 50
  
  validation {
    condition     = var.circuit_breaker_threshold >= 0 && var.circuit_breaker_threshold <= 100
    error_message = "Circuit breaker threshold must be between 0 and 100."
  }
}

variable "circuit_breaker_timeout" {
  description = "Time window in seconds for circuit breaker evaluation"
  type        = number
  default     = 30
  
  validation {
    condition     = var.circuit_breaker_timeout > 0 && var.circuit_breaker_timeout <= 300
    error_message = "Circuit breaker timeout must be between 0 and 300 seconds."
  }
}

variable "west_backend_endpoints" {
  description = "List of Document Intelligence endpoints for West region"
  type = list(object({
    url     = string
    title   = string
    priority = number
  }))
  default = [
    {
      url      = "https://di-west-primary.cognitiveservices.azure.com"
      title    = "Document Intelligence West Primary"
      priority = 1
    },
    {
      url      = "https://di-west-secondary.cognitiveservices.azure.com"
      title    = "Document Intelligence West Secondary"
      priority = 2
    }
  ]
}

variable "north_backend_endpoints" {
  description = "List of Document Intelligence endpoints for North region"
  type = list(object({
    url     = string
    title   = string
    priority = number
  }))
  default = [
    {
      url      = "https://di-north-primary.cognitiveservices.azure.com"
      title    = "Document Intelligence North Primary"
      priority = 1
    },
    {
      url      = "https://di-north-secondary.cognitiveservices.azure.com"
      title    = "Document Intelligence North Secondary"
      priority = 2
    }
  ]
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "Production"
    Solution    = "APIM-DocumentIntelligence"
    ManagedBy   = "Terraform"
  }
}
