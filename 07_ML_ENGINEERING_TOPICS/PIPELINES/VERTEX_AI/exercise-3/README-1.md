1. First open google cloud run functions
![alt text](images/googlecloudrunfuc1.png)

2. Then create a function.
![alt text](images/googlecloudrunfuc2.png)

![alt text](images/image.png)

3. Click on Save and Deploy or edit and deploy

![alt text](images/image-1.png)

4. Click on Test and copy the curl command and try it.
The curl comand will look something like this:

```
curl -X POST https://yoururl \
-H "Authorization: bearer $(gcloud auth print-identity-token)" \
-H "Content-Type: application/json" \
-d '{
  "name": "Developer"
}'
```

It should give you a response.

5. Let's go to `cloud scheduler`
![alt text](images/image-2.png)
We will trigger the cloud function every minute

6. Fill in the form
![alt text](images/cron.png)

Copy this
![alt text](images/image-3.png)

![alt text](images/image-4.png)

After successfully running, it should show up as successful.
![alt text](images/image-5.png)

Logs Can be found in the cloud function.
![alt text](images/image-6.png)