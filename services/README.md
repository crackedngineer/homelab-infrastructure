https://syncbricks.com/proxmox-google-drive-integration-rclone-setup-guide/

# Reconya Installation

```
git clone https://github.com/Dyneteq/reconya.git /opt/reconya
mv reconya.service /etc/systemd/system
```

Reload systemd
```
sudo systemctl daemon-reload
```
3) Start / Stop / Enable Reconya

Start service:
```
sudo systemctl start reconya
```

Stop service:
```
sudo systemctl stop reconya
```

Restart:

```
sudo systemctl restart reconya
```

Enable at boot:
```
sudo systemctl enable reconya
```

Check status:
```
sudo systemctl status reconya
```