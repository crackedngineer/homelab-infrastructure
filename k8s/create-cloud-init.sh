# to be used inside the proxmox terminal

wget https://cloud-images.ubuntu.com/noble/current/noble-server-cloudimg-amd64.img

# Create VM
qm create 9000 --name ubuntu-cloud-template --memory 2048 --net0 virtio,bridge=vmbr0

# Import disk
qm importdisk 9000 noble-server-cloudimg-amd64.img local-lvm

# Attach disk
qm set 9000 --scsihw virtio-scsi-pci --scsi0 local-lvm:vm-9000-disk-0

# Add cloud-init drive
qm set 9000 --ide2 local-lvm:cloudinit

# Configure boot
qm set 9000 --boot c --bootdisk scsi0

# Add serial console
qm set 9000 --serial0 socket --vga serial0

# Enable agent
qm set 9000 --agent enabled=1

# Configure cloud-init
qm set 9000 --ciuser admin
qm set 9000 --cipassword password

ssh-keygen -t ed25519 -C "your_email@example.com"
qm set 9000 --sshkeys ~/.ssh/id_ed25519.pub
qm set 9000 --ipconfig0 ip=dhcp
qm set 9000 --nameserver 8.8.8.8

qm set 9000 --cpu host
qm set 9000 --numa 0

# Convert to template
qm template 9000