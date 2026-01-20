variable "apim_name" {
  description = "Name of the APIM service"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "active_backend" {
  description = "Active backend pool identifier"
  type        = string
}

variable "backend_switch_threshold" {
  description = "Latency threshold for backend switching (seconds)"
  type        = number
}

variable "circuit_breaker_threshold" {
  description = "Error rate percentage to trigger circuit breaker"
  type        = number
}

variable "circuit_breaker_timeout" {
  description = "Circuit breaker evaluation window (seconds)"
  type        = number
}

variable "tags" {
  description = "Tags to apply to named values"
  type        = map(string)
  default     = {}
}
