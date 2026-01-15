# Tailscale helm install

Reference https://youtu.be/XbTUWZt5ljQ?si=eSF2vSfwo69W-b4H

## Create new helm folder
```
helm create tailscale
```

## search taiscale repo version
```
helm search repo tailscale
```

## update dependencies
```
helm dependencies update
```

## check dry run 
```
helm install --dry-run v .
```

## check if all values are replaced in manifest
```
helm install --dry-run v . | grep -i "data:" -A 4
```

## Install tailscale helm chart
```
helm upgrade --install tailscale . \
  --namespace tailscale \
  --create-namespace \
  --set oauth.clientId=$TAILSCALE_CLIENT_ID \
  --set oauth.clientSecret=$TAILSCALE_CLIENT_SECRET
```

## Uninstall tailscale helm chart
```
helm uninstall tailscale -n default
```

## Export kubeconfig cluster with tailscale operator endpoints
```
tailscale configure kubeconfig tailscale-operator
```

## Next Steps
- Multi cluster setup https://tailscale.com/kb/1486/kubernetes-operator-multi-cluster-argocd

# FAQ

## 1. if the error is Error: UPGRADE FAILED: another operation (install/upgrade/rollback) is in progress

1. Check the latest release `kubectl get secret -n tailscale | grep sh.helm.release`
2. Remove the release `kubectl delete secret sh.helm.release.v1.tailscale.v2 -n tailscale`
