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

variable "west_backends" {
  description = "List of backend endpoints for West region"
  type = list(object({
    url      = string
    title    = string
    priority = number
  }))
}

variable "north_backends" {
  description = "List of backend endpoints for North region"
  type = list(object({
    url      = string
    title    = string
    priority = number
  }))
}

variable "tags" {
  description = "Tags to apply to resources"
  type        = map(string)
  default     = {}
}
