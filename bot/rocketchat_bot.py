class RocketchatBot:
    def __init__(self, gateway=None):
        self.gateway = gateway

    def handle_message(self, payload):
        # Minimal echo bot for local testing
        user = payload.get("user", {}).get("_id", "unknown")
        room = payload.get("rid", "default")
        text = payload.get("text", "")
        return {"text": f"echo:{text}", "room": room, "user": user}
