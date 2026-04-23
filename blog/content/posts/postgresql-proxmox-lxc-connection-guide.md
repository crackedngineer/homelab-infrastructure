+++
authors = ["crackedngineer"]
title = "Can't Connect to PostgreSQL in Proxmox LXC? Fix pg_hba.conf"
date = "2023-07-05"
description = "Spun up a PostgreSQL LXC using the Proxmox helper script and immediately hit connection errors from whoDB and psql? One line in pg_hba.conf fixes it."
tags = [
    "postgresql",
    "proxmox",
    "lxc",
    "database",
    "homelab",
    "linux",
    "troubleshooting",
]
reading_time = 3
+++

I used the [Proxmox helper script](https://tteck.github.io/Proxmox/) to spin up a PostgreSQL LXC — quick, clean, works great. But when I tried to connect from **whoDB** (a web-based DB browser I run on the same network) and even from `psql` on another machine, I got nothing. Connection refused. No useful error.

Spent more time than I'd like to admit on this. The fix turned out to be one line.

---

## Why It Happens

PostgreSQL locks down remote access by default. Even if the port is open and the service is running, the database won't accept connections from outside the container unless you explicitly allow them in `pg_hba.conf` — the Host-Based Authentication config file.

Out of the box it only trusts local Unix socket connections. Anything coming over TCP from another machine on your LAN? Rejected.

---

## The Fix

SSH into your PostgreSQL LXC and open the config:

```bash
nano /etc/postgresql/*/main/pg_hba.conf
```

Add this line **at the top**, before the existing rules:

```
host    all     all     192.168.31.0/24     md5
```

Replace `192.168.31.0/24` with your own LAN subnet. The rules are matched top-to-bottom — first match wins — so position matters.

Then restart PostgreSQL:

```bash
systemctl restart postgresql
```

That's it. whoDB connected immediately after.

---

## Quick Breakdown of That Line

```
host    all     all     192.168.31.0/24     md5
│       │       │       │                   │
│       │       │       │                   └─ auth method (md5 password)
│       │       │       └─ source IP range (your LAN)
│       │       └─ any user
│       └─ any database
└─ TCP connection
```

---

## Testing Only (Less Secure)

If you're not sure what your subnet is and just want to verify the fix works, you can temporarily allow any IP:

```
host    all     all     0.0.0.0/0     md5
```

**Remove this once you've confirmed connectivity** and replace it with your actual subnet.

---

## Still Not Working?

A few things to check:

- **`listen_addresses`** — PostgreSQL also needs to listen on the network interface, not just localhost. Check `/etc/postgresql/*/main/postgresql.conf` and make sure this is set:
  ```ini
  listen_addresses = '*'
  ```
  The Proxmox helper script sets this correctly, but worth verifying.

- **Proxmox firewall** — if you have the Proxmox node-level firewall enabled, add an ACCEPT rule for TCP port 5432.

- **Wrong subnet** — run `ip addr` inside the container and `ip addr` on your client machine to confirm they're on the same subnet.

---

Short post, short fix. The Proxmox helper scripts are fantastic for getting services running fast, but the default PostgreSQL security config will always block remote connections until you tell it otherwise.
