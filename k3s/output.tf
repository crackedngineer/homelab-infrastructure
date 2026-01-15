output "control_plane_ips" {
  description = "IP addresses of control plane nodes"
  value = [
    for i in range(var.control_plane_count) : 
    "${var.control_plane_ip_base}${i + var.control_plane_ip_start}"
  ]
}

output "worker_ips" {
  description = "IP addresses of worker nodes"
  value = [
    for i in range(var.worker_count) : 
    "${var.worker_ip_base}${i + var.worker_ip_start}"
  ]
}

output "control_plane_vms" {
  description = "Control plane VM IDs"
  value       = proxmox_vm_qemu.k3s_control_plane[*].vmid
}

output "worker_vms" {
  description = "Worker VM IDs"
  value       = proxmox_vm_qemu.k3s_workers[*].vmid
}

output "ansible_inventory_path" {
  description = "Path to generated Ansible inventory"
  value       = local_file.ansible_inventory.filename
}