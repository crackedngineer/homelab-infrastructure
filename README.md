# homelab-infrastructure

# Prerequisites

1. Generate SSH keys

```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa
```

2. Setup Terraform

```bash
terraform init
terraform apply -var-file="secrets.tfvars"
```