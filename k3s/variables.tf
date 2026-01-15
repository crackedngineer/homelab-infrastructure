variable "proxmox_api_url" {
  description = "Proxmox API URL"
  type        = string
}

variable "proxmox_user" {
  description = "Proxmox user"
  type        = string
}

variable "proxmox_password" {
  description = "Proxmox password"
  type        = string
  sensitive   = true
}

variable "proxmox_tls_insecure" {
  description = "Disable TLS verification"
  type        = bool
  default     = true
}

variable "proxmox_node" {
  description = "Proxmox node name"
  type        = string
}

variable "template_name" {
  description = "Cloud-init template name"
  type        = string
}

variable "storage_pool" {
  description = "Storage pool name"
  type        = string
  default     = "local-lvm"
}

variable "network_bridge" {
  description = "Network bridge"
  type        = string
  default     = "vmbr0"
}

variable "cluster_name" {
  description = "K3s cluster name"
  type        = string
}

variable "control_plane_count" {
  description = "Number of control plane nodes"
  type        = number
  default     = 1
}

variable "control_plane_cpu" {
  description = "CPU cores for control plane"
  type        = number
  default     = 2
}

variable "control_plane_memory" {
  description = "Memory for control plane (MB)"
  type        = number
  default     = 4096
}

variable "control_plane_disk_size" {
  description = "Disk size for control plane"
  type        = string
  default     = "20G"
}

variable "control_plane_ip_base" {
  description = "IP address base for control plane"
  type        = string
}

variable "control_plane_ip_start" {
  description = "Starting number for control plane IPs"
  type        = number
  default     = 10
}

variable "worker_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 2
}

variable "worker_cpu" {
  description = "CPU cores for workers"
  type        = number
  default     = 2
}

variable "worker_memory" {
  description = "Memory for workers (MB)"
  type        = number
  default     = 4096
}

variable "worker_disk_size" {
  description = "Disk size for workers"
  type        = string
  default     = "30G"
}

variable "worker_ip_base" {
  description = "IP address base for workers"
  type        = string
}

variable "worker_ip_start" {
  description = "Starting number for worker IPs"
  type        = number
  default     = 20
}

variable "network_cidr" {
  description = "Network CIDR (e.g., 24)"
  type        = number
  default     = 24
}

variable "gateway" {
  description = "Network gateway"
  type        = string
}

variable "cloud_init_user" {
  description = "Cloud-init user"
  type        = string
  default     = "ubuntu"
}

variable "cloud_init_password" {
  description = "Cloud-init password"
  type        = string
  sensitive   = true
}

variable "ssh_public_key" {
  description = "SSH public key"
  type        = string
}