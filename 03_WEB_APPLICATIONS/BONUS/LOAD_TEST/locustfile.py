from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(0.1, 0.2)  # Adjust wait time to control request rate

    @task
    def send_chat_message(self):
        payload = {
            "message": "Hello, how are you?"
        }
        self.client.post("/chat", json=payload)