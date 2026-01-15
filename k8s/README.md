terraform install --upgrade
terraform plan -out=.tfplan
terraform apply ".tfplan"
terraform destroy