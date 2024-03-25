from locust import HttpUser, task, between

class ChatbotUser(HttpUser):
    wait_time = between(5, 8)  # Users will wait between 5 and 8 seconds before each task

    @task
    def send_message(self):
        self.client.post("/bucc-7b-bot", json={"message": "Hello, chatbot!"})
