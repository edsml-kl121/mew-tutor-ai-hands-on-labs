`docker login`

`docker build -t <your-dockerhub-username>/<image-name>:<tag> .`


`docker build -t <your-dockerhub-username>/frontend:latest .`
`docker tag frontend <your-dockerhub-username>/frontend:latest`
`docker push <your-dockerhub-username>/frontend:latest`

verify in dockerhub.