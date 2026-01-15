[control_plane]
%{ for ip in control_plane_ips ~}
${ip} ansible_user=${ansible_user}
%{ endfor ~}

[workers]
%{ for ip in worker_ips ~}
${ip} ansible_user=${ansible_user}
%{ endfor ~}

[k3s_cluster:children]
control_plane
workers

[k3s_cluster:vars]
ansible_python_interpreter=/usr/bin/python3
ansible_ssh_common_args='-o StrictHostKeyChecking=no'