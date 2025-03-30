# Main Tasks
1. `pip install -r requirement.txt`

2. `streamlit run app.py`

2. Update the website to your portfolio.

3. Read https://docs.streamlit.io/develop/api-reference



## Docker Commands

1. Sign up for dockerhub.
`docker login`

2. Build your image
`docker build -t <your-dockerhub-username>/frontend:latest .`
example:

3. Run it to test it
option1: `docker run -p 8501:8501 myusername/frontend:latest`
option2: `docker run -d -p 8501:8501 myusername/frontend:latest` ## Detatched meaning running in the background
option3: `docker run -p 8501:8501 -it --rm myusername/frontend:latest sh`

4. Push image to registry
`docker push <your-dockerhub-username>/frontend:latest`

## Optional. you can also tag your image like below:
`docker build -t frontend .`
`docker tag frontend <your-dockerhub-username>/frontend:latest`



Extra commands
`docker images` -> See images
`docker ps` -> Check Containers running
`docker stop <containerid>` -> Stop running container
`docker rmi <imgid>` -> Remove Image ID
`docker rm <containerid>` -> Remove stopped container.
Test `docker run -d --name my-nginx -p 8080:80 nginx`
verify in dockerhub