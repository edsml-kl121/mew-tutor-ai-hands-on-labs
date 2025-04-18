#!/bin/bash
# Script to deploy the application to Kubernetes with separate namespaces for FE and BE

# Step 1: Build Docker images
# echo "Building Docker images..."

# podman build --arch amd64 -t u1800085/backend:amd64 BE
# podman build --arch amd64 -t u1800085/frontend:amd64 BE
podman build --arch arm64 -t backend:latest BE
podman build --arch arm64 -t frontend:latest FE

# echo "Tagging images for registry..."
podman tag backend:latest u1800085/backend:latest
podman tag frontend:latest u1800085/frontend:latest

podman push u1800085/backend:latest
podman push u1800085/frontend:latest


# Step 2: Create namespaces if they don't exist
echo "Creating namespaces..."
kubectl create namespace frontend --dry-run=client -o yaml | kubectl apply -f -
kubectl create namespace backend --dry-run=client -o yaml | kubectl apply -f -

# Step 3: Create Base64 encoded API key for the secret
echo "Creating Kubernetes secrets in both namespaces..."
API_KEY="YOUR_API_KEY"
ENCODED_API_KEY=$(echo -n $API_KEY | base64)

# (Optional) Inject secret into secrets.yaml before applying, if required
# sed -i "s/BASE64_ENCODED_API_KEY_HERE/$ENCODED_API_KEY/g" kubernetes/secrets.yaml

kubectl apply -f kubernetes/secrets.yaml -n frontend
kubectl apply -f kubernetes/secrets.yaml -n backend

# Step 4: Apply Kubernetes configurations
echo "Applying Kubernetes configurations..."
kubectl apply -f kubernetes/backend-deployment.yaml -n backend
kubectl apply -f kubernetes/frontend-deployment.yaml -n frontend

# Step 5: Check deployment status
echo "Checking deployment status..."
kubectl get deployments -n backend
kubectl get deployments -n frontend
kubectl get pods -n backend
kubectl get pods -n frontend
kubectl get services -n frontend

# Optional for Minikube
# echo "Frontend URL: $(minikube service frontend-service -n frontend --url)"

echo "✅ Deployment completed."
echo "🌐 Access the frontend via LoadBalancer external IP or Minikube URL (if using Minikube)."