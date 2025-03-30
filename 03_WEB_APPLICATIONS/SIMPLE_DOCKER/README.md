## Docker Commands

## Step 1: Sign up for dockerhub.
`docker login`

## Option 1:
`docker build -t echo-app`
`docker tag echo-app <username>/echo-app:latest`
`docker push <username>/echo-app:latest`

## Option 2:
`docker build <username>/echo-app:latest`
`docker push <username>/echo-app:latest`

## Running the image
`docker images`
`docker run <image_id>`

## Inspect inside:
`docker run -it --rm <image_id> sh`

Extra commands
`docker images` -> See images
`docker ps` -> Check Containers running
`docker stop <containerid>` -> Stop running container
`docker rmi <imgid>` -> Remove Image ID
`docker rm <containerid>` -> Remove stopped container.
Test `docker run -d --name my-nginx -p 8080:80 nginx`
verify in dockerhub