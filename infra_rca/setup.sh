#! /bin/bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y curl wget git vim net-tools htop jq python3 python3-venv

curl -sfL https://get.k3s.io | sh -

sudo systemctl status k3s


mkdir -p ~/.kube
sudo cp /etc/rancher/k3s/k3s.yaml ~/.kube/config
sudo chown $(id -u):$(id -g) ~/.kube/config
export KUBECONFIG=~/.kube/config


kubectl get nodes -o wide
kubectl get pods -A

kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

kubectl get deployment metrics-server -n kube-system
kubectl top nodes

## Scenario setup

# Create demo namespace
kubectl create ns demo

# Run all test pods
kubectl run badimage --image=nginx:doesnotexist --restart=Never -n demo
kubectl run crashloop --image=busybox --restart=Always -n demo --command -- sh -c "sleep 2; exit 1" 


kubectl run highmem \
  -n demo \
  --image=python:3.9 \
  --restart=Never \
  --overrides='{
    "spec": {
      "containers": [{
        "name": "highmem",
        "image": "python:3.9",
        "resources": {
          "requests": {"memory": "50Mi"},
          "limits": {"memory": "100Mi"}
        },
        "command": ["python3", "-c", "a=[\"x\"*1024*1024 for _ in range(200)]"]
      }]
    }
  }'


kubectl run badprobe \
  -n demo \
  --image=nginx \
  --port=80 \
  --restart=Never \
  --overrides='{
    "spec": {
      "containers": [{
        "name": "badprobe",
        "image": "nginx",
        "ports": [{"containerPort": 80}],
        "livenessProbe": {
          "httpGet": {"path": "/", "port": 9999},
          "initialDelaySeconds": 3,
          "periodSeconds": 5
        }
      }]
    }
  }'
kubectl run badnetwork --image=busybox --restart=Never -n demo --command -- nslookup notarealhost.default.svc.cluster.local
# kubectl run cpuhog --image=busybox --restart=Never --requests='cpu=50m' --limits='cpu=100m' --command -- sh -c "while true; do :; done"
