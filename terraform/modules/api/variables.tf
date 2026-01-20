variable "apim_name" {
  description = "Name of the APIM service"
  type        = string
}

variable "apim_id" {
  description = "ID of the APIM service"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "api_path" {
  description = "Base path for the API"
  type        = string
  default     = "doc"
}
