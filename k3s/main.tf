terraform {
  required_providers {
    proxmox = {
      source  = "telmate/proxmox"
      version = "3.0.2-rc01"
    }
  }
}

provider "proxmox" {
  pm_api_url      = var.proxmox_api_url
  pm_user         = var.proxmox_user
  pm_password     = var.proxmox_password
  pm_tls_insecure = var.proxmox_tls_insecure
}

locals {
  vm_name = var.template_name
  pve_node = var.proxmox_node
  iso_storage_pool = var.storage_pool
}

resource "proxmox_cloud_init_disk" "ci" {
  name      = local.vm_name
  pve_node  = local.pve_node
  storage   = local.iso_storage_pool

  meta_data = yamlencode({
    instance_id    = sha1(local.vm_name)
    local-hostname = local.vm_name
  })

  user_data = <<-EOT
  #cloud-config
  users:
    - name: var .cloud_init_user
  password: var.cloud_init_password
  ssh_authorized_keys:
    - var.ssh_public_key
  EOT

  network_config = yamlencode({
    version = 1
    config = [{
      type = "physical"
      name = var.network_bridge
      subnets = [{
        type            = "static"
        address         = "192.168.1.100/24"
        gateway         = "192.168.1.1"
        dns_nameservers = [
          "1.1.1.1", 
          "8.8.8.8"
          ]
      }]
    }]
  })
}

# Control Plane Nodes
resource "proxmox_vm_qemu" "k3s_control_plane" {
  count       = var.control_plane_count
  name        = "${var.cluster_name}-cp-${count.index + 1}"
  target_node = var.proxmox_node
  # clone       = var.template_name

  agent   = 1
  os_type = "cloud-init"
  cpu {
    cores = var.control_plane_cpu
    sockets = 1
  }
  memory = var.control_plane_memory

  disk {
    slot    = "scsi0"
    size    = var.control_plane_disk_size
    type    = "disk"
    storage = var.storage_pool
  }

  disks {
    scsi {
      scsi0 {
        cdrom {
          iso = "${proxmox_cloud_init_disk.ci.id}"
        }
      }
    }
  }

  network {
    id     = 0
    model  = "virtio"
    bridge = var.network_bridge
  }

  ipconfig0 = "ip=${var.control_plane_ip_base}${count.index + var.control_plane_ip_start}/${var.network_cidr},gw=${var.gateway}"

  ciuser     = var.cloud_init_user
  cipassword = var.cloud_init_password
  sshkeys    = var.ssh_public_key

  lifecycle {
    ignore_changes = [
      network,
    ]
  }
}

# Worker Nodes
resource "proxmox_vm_qemu" "k3s_workers" {
  count       = var.worker_count
  name        = "${var.cluster_name}-worker-${count.index + 1}"
  target_node = var.proxmox_node
  # clone       = var.template_name

  agent   = 1
  os_type = "cloud-init"
  cpu {
    cores   = var.worker_cpu
    sockets = 1
  }
  memory = var.worker_memory

  disk {
    slot    = "scsi0"
    size    = var.worker_disk_size
    type    = "disk"
    storage = var.storage_pool
    iso = "HDD-Storage:iso/ubuntu-24.04.3-live-server-amd64.iso"
  }

  network {
    id     = 0
    model  = "virtio"
    bridge = var.network_bridge
  }

  ipconfig0 = "ip=${var.worker_ip_base}${count.index + var.worker_ip_start}/${var.network_cidr},gw=${var.gateway}"

  ciuser     = var.cloud_init_user
  cipassword = var.cloud_init_password
  sshkeys    = var.ssh_public_key

  lifecycle {
    ignore_changes = [
      network,
    ]
  }
}

# Generate Ansible Inventory
resource "local_file" "ansible_inventory" {
  content = templatefile("${path.module}/templates/inventory.tpl", {
    control_plane_ips = [for i in range(var.control_plane_count) : "${var.control_plane_ip_base}${i + var.control_plane_ip_start}"]
    worker_ips        = [for i in range(var.worker_count) : "${var.worker_ip_base}${i + var.worker_ip_start}"]
    ansible_user      = var.cloud_init_user
  })
  filename = "${path.module}/ansible/inventory.ini"

  depends_on = [
    proxmox_vm_qemu.k3s_control_plane,
    proxmox_vm_qemu.k3s_workers
  ]
}
