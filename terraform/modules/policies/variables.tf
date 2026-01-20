variable "apim_name" {
  description = "Name of the APIM service"
  type        = string
}

variable "resource_group_name" {
  description = "Resource group name"
  type        = string
}

variable "api_name" {
  description = "Name of the API"
  type        = string
}

variable "west_pool_id" {
  description = "Backend pool ID for West region"
  type        = string
}

variable "north_pool_id" {
  description = "Backend pool ID for North region"
  type        = string
}
