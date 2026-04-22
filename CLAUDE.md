# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## MCP Tools: code-review-graph

**IMPORTANT: This project has a knowledge graph. ALWAYS use the
code-review-graph MCP tools BEFORE using Grep/Glob/Read to explore
the codebase.** The graph is faster, cheaper (fewer tokens), and gives
you structural context (callers, dependents, test coverage) that file
scanning cannot.

### When to use graph tools FIRST

- **Exploring code**: `semantic_search_nodes` or `query_graph` instead of Grep
- **Understanding impact**: `get_impact_radius` instead of manually tracing imports
- **Code review**: `detect_changes` + `get_review_context` instead of reading entire files
- **Finding relationships**: `query_graph` with callers_of/callees_of/imports_of/tests_for
- **Architecture questions**: `get_architecture_overview` + `list_communities`

Fall back to Grep/Glob/Read **only** when the graph doesn't cover what you need.

### Key Tools

| Tool | Use when |
|------|----------|
| `detect_changes` | Reviewing code changes — gives risk-scored analysis |
| `get_review_context` | Need source snippets for review — token-efficient |
| `get_impact_radius` | Understanding blast radius of a change |
| `get_affected_flows` | Finding which execution paths are impacted |
| `query_graph` | Tracing callers, callees, imports, tests, dependencies |
| `semantic_search_nodes` | Finding functions/classes by name or keyword |
| `get_architecture_overview` | Understanding high-level codebase structure |
| `refactor_tool` | Planning renames, finding dead code |

### Workflow

1. The graph auto-updates on file changes (via hooks).
2. Use `detect_changes` for code review.
3. Use `get_affected_flows` to understand impact.
4. Use `query_graph` pattern="tests_for" to check coverage.

---

## Repository Overview

This is a **homelab infrastructure-as-code** repository managing a Proxmox-based home server environment. It covers VM/container provisioning (Terraform), Kubernetes clusters (k3s and Talos), Docker Compose stacks, and utility scripts.

### Top-level structure

| Directory | Purpose |
|-----------|---------|
| `agno-assistant/` | Terraform + Ansible to provision an LXC container on Proxmox |
| `docker-compose/` | Docker Compose stacks for self-hosted services |
| `k3s/` | Terraform to provision a k3s cluster on Proxmox |
| `k8s/` | Talos Linux Kubernetes cluster (Terraform + manifests) |
| `scripts/` | Utility Python/Bash scripts |
| `services/` | Systemd service files (rclone, reconya) |
| `data/` | Misc data assets |

---

## Terraform

Secrets are **never** committed. Each Terraform directory has a `secrets.tfvars` (gitignored) and a `credentials.auto.tfvars`. Load secrets then apply:

```bash
terraform init
terraform apply -var-file="secrets.tfvars"
```

Two Proxmox providers are in use:
- `Telmate/proxmox` (k3s, agno-assistant) — older provider, use `pm_*` variables
- `bpg/proxmox` (k8s) — newer provider

---

## Docker Compose stacks

Each stack lives in `docker-compose/<service>/`. Run from that directory:

```bash
docker compose up -d
docker compose down
docker compose logs -f
```

Key stacks:
- **monitoring** — Prometheus + Grafana + Pihole exporter. Requires env vars `PIHOLE_HOSTNAME` and `PIHOLE_PASSWORD`.
- **kafka** — KRaft-mode Kafka + Kafdrop (`:9090`) + kafka-ui (`:8080`). Kafka listens on `:9092` externally.
- **proxmox-exporter** — Python Prometheus exporter for Proxmox VMs/LXCs (port `9221`). Run the Python script directly: `python python/README.md` is the source; install deps with `pip install proxmoxer prometheus_client`.
- **servarr** — *arr stack. Requires Portainer pre-installed (see `servarr/README.md`).
- **nextcloud**, **navidrome**, **waha**, **homer**, **omni-tools**, **rss-feed**, **agno** — standalone compose stacks.

---

## Kubernetes (Talos)

Cluster config lives in `k8s/talos/`. Workflow:

```bash
# Load env
export $(grep -v '^#' .env | xargs)

# Generate cluster config
talosctl gen config proxmox-k8s-cluster https://$CONTROL_PLANE_IP:6443 -o .

# Apply configs
talosctl apply-config --nodes $CONTROL_PLANE_IP --file controlplane.yaml --insecure
talosctl apply-config --nodes $WORKER_NODE_IP --file worker.yaml --insecure

# Bootstrap etcd
talosctl config endpoint $CONTROL_PLANE_IP
talosctl config node $CONTROL_PLANE_IP
talosctl bootstrap

# Get kubeconfig
talosctl kubeconfig .
```

GitOps via **ArgoCD** (`k8s/argocd/`). Install:
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode
```

Networking uses **MetalLB** + **Tailscale operator** via Helm (`k8s/helm/`). MetalLB pool config: `k8s/metallb-pool.yaml`.

---

## Scripts

All scripts are in `scripts/` and are standalone Python files. They read credentials from environment variables or a `.env` file:

```bash
export $(grep -v '^#' .env | xargs)
```

| Script | Purpose |
|--------|---------|
| `npm_ip_sync.py` | Syncs LXC container IPs to Nginx Proxy Manager hosts via Proxmox API |
| `storage_details.sh` | Reports Proxmox storage usage |
| `startup.sh` | Node startup tasks |
| `cartoon_download_script.py` | Downloads cartoons via yt-dlp |
| `saregama_carvaan_old_hindi_songs.py` | Downloads Hindi songs playlist |
| `satyajit_ray_films_downloader.py` | Downloads Satyajit Ray films |
| `video_compression.py` | Batch video compression |
| `yt_trimmer.py` | Downloads trimmed YouTube clips |

Python deps for scripts using Proxmox API: `pip install proxmoxer requests`

---

## Services (Proxmox host systemd)

- `services/rclone-gdrive.service` — mounts Google Drive via rclone on the Proxmox host
- `services/reconya.service` — runs Reconya network scanner

Deploy by copying to `/etc/systemd/system/` and running `systemctl daemon-reload && systemctl enable --now <service>`.
