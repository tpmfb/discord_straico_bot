from typing import Dict, List, Optional
import logging

class ConversationHistory:
    def __init__(self, max_history: int = 50):
        self.history: Dict[int, List[Dict]] = {}
        self.max_history = max_history
        self.logger = logging.getLogger(__name__)

    def add_message(self, channel_id: int, role: str, content: str, username: str = None):
        if channel_id not in self.history:
            self.history[channel_id] = []

        message = {
            "role": role,
            "content": content
        }
        if username:
            message["name"] = username

        self.history[channel_id].append(message)

        if len(self.history[channel_id]) > self.max_history:
            self.history[channel_id] = self.history[channel_id][-self.max_history:]

        self.logger.debug(f"Added message to channel {channel_id}: {role}")

    def get_history(self, channel_id: int) -> List[Dict]:
        return self.history.get(channel_id, [])

    def clear_history(self, channel_id: int):
        if channel_id in self.history:
            del self.history[channel_id]
            self.logger.info(f"Cleared history for channel {channel_id}")

    def get_channel_count(self) -> int:
        return len(self.history)

    def get_total_messages(self) -> int:
        return sum(len(messages) for messages in self.history.values())