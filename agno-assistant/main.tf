terraform {
  required_providers {
    proxmox = {
      source  = "Telmate/proxmox"
      version = "3.0.2-rc01"
    }
  }
}


provider "proxmox" {
  pm_api_url      = "https://${var.proxmox_ip}/api2/json"
  pm_user         = "root@pam"
  pm_password     = var.proxmox_password
  pm_tls_insecure = true
}

resource "proxmox_lxc" "agno-assistant" {
  target_node  = "pve"
  hostname     = "agno-assistant"
  ostemplate   = "HDD-Storage:vztmpl/debian-12-standard_12.7-1_amd64.tar.zst"
  password     = var.container_password
  cores        = 2
  memory       = 2048
  swap         = 512
  unprivileged = true
  start        = true

  rootfs {
    size    = "8G"
    storage = "local-lvm"
  }

  network {
    name   = "eth0"
    bridge = "vmbr0"
    ip     = "192.168.31.150/24"
    gw     = "192.168.31.1"
  }

  features {
    nesting = true
  }

  ssh_public_keys = file("~/.ssh/id_rsa.pub")

  # Provision script to install Node, clone repo, and start Next.js
  provisioner "remote-exec" {
    inline = ["echo 'Cool, we are ready for provisioning'"]

    connection {
      type        = "ssh"
      user        = "root"
      host        = "192.168.31.150"
      private_key = file("~/.ssh/id_rsa")
      timeout     = "5m"
    }
  }

  provisioner "local-exec" {
    command = "ANSIBLE_HOST_KEY_CHECKING=False ansible-playbook -i ansible/inventory.ini ansible/site.yml"
  }
}
