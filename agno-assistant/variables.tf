variable "proxmox_password" {
  type      = string
  sensitive = true
}

variable "container_password" {
  type    = string
  default = "changeme"
}

variable "proxmox_ip" {
  type      = string
  sensitive = true
}
