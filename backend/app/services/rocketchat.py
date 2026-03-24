from typing import Optional


class RocketChatGateway:
    def __init__(self, url: str):
        self.url = url

    def send_message(self, room_id: str, user_id: str, text: str) -> None:
        # Placeholder: in MVP this would POST to Rocket.Chat REST API or gateway
        print(f"[RC Gateway] to {room_id}@{user_id}: {text}")
