variable "subscription_id" {
  description = "Azure subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "aks-platform-rg"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "polandcentral"
}

variable "prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "softdevaks"
}
