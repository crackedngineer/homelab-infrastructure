# Talos Linux Setup

## System Requirements
https://docs.siderolabs.com/talos/v1.12/getting-started/system-requirements

## Load Env
```
export $(grep -v '^#' .env | xargs)
```

## Generate CLuster Config
```
talosctl gen config promxox-k8s-cluster https://$CONTROL_PLANE_IP:6443  -o .
```

## Configure Control Panel
```
talosctl apply-config --nodes $CONTROL_PLANE_IP --file controlplane.yaml --insecure
```

## Configure Worker Node
```
talosctl apply-config --nodes $WORKER_NODE_IP --file worker.yaml --insecure
```

## etcd setup
```
talosctl config endpoint $CONTROL_PLANE_IP
talosctl config node $CONTROL_PLANE_IP
talosctl bootstrap
talosctl dmesg
```

## Generate Kubeconfig
```
talosctl kubeconfig .
```

## check health of node
```
talosctl -n $CONTROL_PLANE_IP health
```

## get talosctl members
```
talosctl -n $CONTROL_PLANE_IP get members
```