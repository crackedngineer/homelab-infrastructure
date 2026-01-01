"""
export $(cat .env | xargs)

pip install -qU proxmoxer

For WSL
pip install -qU proxmoxer --break-system-packages
"""

import os
import requests
from proxmoxer import ProxmoxAPI

PROXMOX_HOST = str(os.getenv("PROXMOX_HOST")).strip()
PROXMOX_USER = str(os.getenv("PROXMOX_USER", "")).strip()
PROXMOX_PASSWORD = str(os.getenv("PROXMOX_PASSWORD", "")).strip()

NPM_HOST = str(os.getenv("NPM_HOST", "")).strip()
NPM_USER = str(os.getenv("NPM_USER", "")).strip()
NPM_PASSWORD = str(os.getenv("NPM_PASSWORD", "")).strip()


proxmox = ProxmoxAPI(
    host=str(PROXMOX_HOST), user=PROXMOX_USER, password=PROXMOX_PASSWORD, verify_ssl=False
)

LXC_NPM_DOMAIN_MAP = {
    "influxdb": "influxdb",
    "*.servarr": "servarr",
    "myspeed": "myspeed",
    "stirling-pdf": "stirling-pdf",
    "openwebui": "openwebui",
    "n8n": "n8n",
    "jellyfin": "jellyfin",
    "immich": "immich",
    "komodo": "komodo",
    "ai-agent": "komodo",
    "homer": "komodo",
    "litellm": "komodo",
    "omni-tools": "komodo",
    "npm": "nginxproxymanager",
    "grafana": "grafana",
    "nextcloud": "nextcloud-aio",
    "nc-aio": "nextcloud-aio",
    "prometheus": "prometheus",
    "vaultwarden": "alpine-vaultwarden",
    "homeassistant": "homeassistant",
    "cosmos": "cosmos",
    "pihole": "pihole",
}


class NpmProvider(object):
    def __init__(self, host: str, user: str, password: str) -> None:
        self.host = host
        access_token = self.__login(user, password)
        self.headers = {"Authorization": f"Bearer {access_token}"}

    def __login(self, user: str, password: str) -> str:
        response = requests.post(
            f"{self.host}/api/tokens",
            {
                "identity": user,
                "secret": password,
            },
            verify=False
        )
        return response.json()["token"]

    def get_all_proxy(self) -> dict:
        response = requests.get(
            f"{self.host}/api/nginx/proxy-hosts/", headers=self.headers, verify=False
        )
        if not response.ok:
            raise Exception("Failed to fetch proxy")
        return response.json()

    def update_proxy_ip(self, proxy, ip: str):
        payload = {"forward_host": ip}
        response = requests.put(
            f"{self.host}/api/nginx/proxy-hosts/{proxy["id"]}",
            headers=self.headers,
            data=payload,
            verify=False
        )
        if not response.ok:
            raise Exception("Failed to update proxy")
        return response.json()


if __name__ == "__main__":
    lxc_ips = {}

    npm_obj = NpmProvider(
        host=str(NPM_HOST), user=str(NPM_USER), password=str(NPM_PASSWORD)
    )

    for node in proxmox.nodes.get() or []:
        node_name = node["node"]
        for lxc in proxmox.nodes(node_name).lxc.get() or []:
            vmid, lxc_name = lxc["vmid"], lxc["name"]
            interfaces = proxmox.nodes(node_name).lxc(vmid).interfaces.get() or {}
            ip = interfaces[1].get("inet", {}).split("/")[0]
            for domain, lxc in LXC_NPM_DOMAIN_MAP.items():
                if lxc == lxc_name:
                    lxc_ips[domain] = ip

    # Fetch updated NPM IPs
    npm_proxy = npm_obj.get_all_proxy()
    for proxy in npm_proxy:
        for domain, lxc_ip in lxc_ips.items():
            if (
                f"{domain}.home.lan" in proxy["domain_names"]
                and lxc_ip != proxy["forward_host"]
            ):
                npm_obj.update_proxy_ip(proxy, lxc_ip)
                print(f"Forwarded {domain} to {lxc_ip}")
