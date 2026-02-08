#!/usr/bin/env python3
"""
Proxmox Prometheus Exporter
Exports VM/Container metrics including IP addresses, memory, and mounted drives
"""
import os
import time
import urllib3
from prometheus_client import start_http_server, Gauge, Info
from proxmoxer import ProxmoxAPI
import argparse
import logging

# Disable SSL warnings if using self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Define Prometheus metrics
vm_memory_bytes = Gauge('proxmox_vm_memory_bytes', 
                        'VM/Container memory in bytes', 
                        ['node', 'vmid', 'name', 'type'])

vm_memory_max_bytes = Gauge('proxmox_vm_memory_max_bytes', 
                            'VM/Container maximum memory in bytes', 
                            ['node', 'vmid', 'name', 'type'])

vm_memory_usage_percent = Gauge('proxmox_vm_memory_usage_percent', 
                                'VM/Container memory usage percentage', 
                                ['node', 'vmid', 'name', 'type'])

vm_ip_info = Info('proxmox_vm_ip', 
                  'VM/Container IP address information', 
                  ['node', 'vmid', 'name', 'type'])

vm_disk_info = Info('proxmox_vm_disk', 
                    'VM/Container disk/drive information', 
                    ['node', 'vmid', 'name', 'type', 'disk'])

vm_disk_size_bytes = Gauge('proxmox_vm_disk_size_bytes', 
                           'VM/Container disk size in bytes', 
                           ['node', 'vmid', 'name', 'type', 'disk'])

vm_disk_used_bytes = Gauge('proxmox_vm_disk_used_bytes', 
                           'VM/Container disk used space in bytes', 
                           ['node', 'vmid', 'name', 'type', 'disk'])


class ProxmoxExporter:
    def __init__(self, host, user, password, verify_ssl=False):
        """Initialize Proxmox API connection"""
        try:
            self.proxmox = ProxmoxAPI(
                host,
                user=user,
                password=password,
                verify_ssl=verify_ssl
            )
            logger.info(f"Connected to Proxmox host: {host}")
        except Exception as e:
            logger.error(f"Failed to connect to Proxmox: {e}")
            raise

    def get_vm_ip_addresses(self, node, vmid, vm_type):
        """Get IP addresses for a VM or container"""
        ip_addresses = []
        try:
            if vm_type == 'qemu':  # VM
                # Get agent network interfaces
                try:
                    agent_info = self.proxmox.nodes(node).qemu(vmid).agent.get('network-get-interfaces')
                    if agent_info:
                        for interface in agent_info.get('result', []):
                            if 'ip-addresses' in interface:
                                for ip in interface['ip-addresses']:
                                    if ip.get('ip-address-type') == 'ipv4':
                                        ip_addresses.append(ip.get('ip-address'))
                except:
                    pass
            else:  # LXC Container
                try:
                    interfaces = self.proxmox.nodes(node).lxc(vmid).interfaces.get()
                    # Parse network interfaces
                    if interfaces:
                        ip = interfaces[1].get("inet", {}).split("/")[0]
                        ip_addresses.append(ip)
                    # if config:
                    #     for key, value in config.items():
                    #         if key.startswith('net'):
                    #             if 'ip=' in value:
                    #                 ip = value.split('ip=')[1].split(',')[0].split('/')[0]
                    #                 ip_addresses.append(ip)
                except:
                    pass
        except Exception as e:
            logger.debug(f"Could not get IP for {vm_type}/{vmid}: {e}")
        
        return ip_addresses

    def get_vm_disks(self, node, vmid, vm_type):
        """Get disk information for a VM or container"""
        disks = {}
        try:
            if vm_type == 'qemu':  # VM
                config = self.proxmox.nodes(node).qemu(vmid).config.get()
                if config:
                    for key, value in config.items():
                        if key.startswith(('scsi', 'ide', 'sata', 'virtio')):
                            disks[key] = value
            else:  # LXC Container
                config = self.proxmox.nodes(node).lxc(vmid).config.get()
                if config:
                    if 'rootfs' in config:
                        disks['rootfs'] = config['rootfs']
                    for key, value in config.items():
                        if key.startswith('mp'):
                            disks[key] = value
        except Exception as e:
            logger.debug(f"Could not get disks for {vm_type}/{vmid}: {e}")
        
        return disks

    def collect_metrics(self):
        """Collect metrics from all VMs and containers"""
        logger.info("Collecting metrics from Proxmox...")
        
        try:
            # Get all nodes
            nodes = self.proxmox.nodes.get()
            if nodes:
                for node in nodes:
                    node_name = node['node']
                    logger.debug(f"Processing node: {node_name}")
                    
                    # Get VMs (qemu)
                    try:
                        vms = self.proxmox.nodes(node_name).qemu.get()
                        if vms:
                            for vm in vms:
                                self.process_resource(node_name, vm, 'qemu')
                    except Exception as e:
                        logger.error(f"Error processing VMs on {node_name}: {e}")
                    
                    # Get Containers (lxc)
                    try:
                        containers = self.proxmox.nodes(node_name).lxc.get()
                        if containers:
                            for container in containers:
                                self.process_resource(node_name, container, 'lxc')
                    except Exception as e:
                        logger.error(f"Error processing containers on {node_name}: {e}")
                    
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")

    def process_resource(self, node_name, resource, resource_type):
        """Process a single VM or container"""
        vmid = str(resource['vmid'])
        name = resource.get('name', f'{resource_type}-{vmid}')
        status = resource.get('status', 'unknown')
        
        logger.debug(f"Processing {resource_type}/{vmid} ({name}) - status: {status}")
        
        # Only collect metrics for running resources
        if status != 'running':
            return
        
        # Memory metrics
        mem = resource.get('mem', 0)
        maxmem = resource.get('maxmem', 1)
        
        vm_memory_bytes.labels(
            node=node_name,
            vmid=vmid,
            name=name,
            type=resource_type
        ).set(mem)
        
        vm_memory_max_bytes.labels(
            node=node_name,
            vmid=vmid,
            name=name,
            type=resource_type
        ).set(maxmem)
        
        mem_percent = (mem / maxmem * 100) if maxmem > 0 else 0
        vm_memory_usage_percent.labels(
            node=node_name,
            vmid=vmid,
            name=name,
            type=resource_type
        ).set(mem_percent)
        
        # IP addresses
        ip_addresses = self.get_vm_ip_addresses(node_name, vmid, resource_type)
        if ip_addresses:
            vm_ip_info.labels(
                node=node_name,
                vmid=vmid,
                name=name,
                type=resource_type
            ).info({
                'ip_addresses': ','.join(ip_addresses),
                'primary_ip': ip_addresses[0] if ip_addresses else 'none'
            })
        
        # Disk information
        disks = self.get_vm_disks(node_name, vmid, resource_type)
        for disk_name, disk_info in disks.items():
            vm_disk_info.labels(
                node=node_name,
                vmid=vmid,
                name=name,
                type=resource_type,
                disk=disk_name
            ).info({
                'disk_config': str(disk_info)
            })
            
            # Try to get disk usage if available
            try:
                if resource_type == 'qemu':
                    status = self.proxmox.nodes(node_name).qemu(vmid).status.current.get()
                else:
                    status = self.proxmox.nodes(node_name).lxc(vmid).status.current.get()
                
                if status:
                    disk_used = status.get('disk', 0)
                    disk_max = status.get('maxdisk', 0)
                
                if disk_max > 0:
                    vm_disk_size_bytes.labels(
                        node=node_name,
                        vmid=vmid,
                        name=name,
                        type=resource_type,
                        disk='total'
                    ).set(disk_max)
                    
                    vm_disk_used_bytes.labels(
                        node=node_name,
                        vmid=vmid,
                        name=name,
                        type=resource_type,
                        disk='total'
                    ).set(disk_used)
            except:
                pass


def main():
    parser = argparse.ArgumentParser(description='Proxmox Prometheus Exporter')
    # parser.add_argument('--host', required=True, help='Proxmox host (IP or hostname)')
    # parser.add_argument('--user', required=True, help='Proxmox user (e.g., root@pam)')
    # parser.add_argument('--password', required=True, help='Proxmox password')
    # parser.add_argument('--port', type=int, default=9221, help='Exporter port (default: 9221)')
    # parser.add_argument('--interval', type=int, default=60, help='Collection interval in seconds (default: 60)')
    # parser.add_argument('--verify-ssl', action='store_true', help='Verify SSL certificates')
    
    # args = parser.parse_args()
    
    # Initialize exporter
    exporter = ProxmoxExporter(
        host=os.getenv("PROXMOX_HOST"),
        user=os.getenv("PROXMOX_USER"),
        password=os.getenv("PROXMOX_PASSWORD"),
        verify_ssl=False  # Default to False for simplicity in Docker environment
    )
    
    # Start Prometheus HTTP server
    start_http_server(9221)
    logger.info(f"Prometheus exporter started on port 9221")
    logger.info(f"Metrics available at http://localhost:9221/metrics")
    
    # Collection loop
    while True:
        try:
            exporter.collect_metrics()
            logger.info(f"Metrics collected successfully.")
        except Exception as e:
            logger.error(f"Error in collection loop: {e}")
        
        time.sleep(60)


if __name__ == '__main__':
    main()