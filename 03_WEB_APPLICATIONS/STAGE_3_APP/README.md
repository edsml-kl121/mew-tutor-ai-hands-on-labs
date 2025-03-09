Navigate to the backend folder:


```
cd backend
```
Build the Docker image:
```
docker build -t backend .
```
Run the backend container:

```
docker run -d --name backend -p 5000:5000
```

Step 2: Build the Frontend Container
Navigate to the frontend folder:
```
cd ../frontend
```
Build the Docker image:

```
docker build -t frontend .
```
Run the frontend container:

``````
docker run -d --name frontend -p 8501:8501 
```