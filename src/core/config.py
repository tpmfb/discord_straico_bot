import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from dotenv import load_dotenv
from .errors import ConfigurationError

@dataclass
class Config:
    discord_token: str = ""
    straico_api_key: str = ""
    command_prefix: str = "!"
    log_level: str = "INFO"
    log_file: Optional[str] = None
    max_history_per_channel: int = 50
    default_chat_model: str = "openai/gpt-5"
    max_message_length: int = 2000
    api_base_url: str = "https://api.straico.com"
    auto_response_channels: set = field(default_factory=set)
    user_models: Dict[int, str] = field(default_factory=dict)

    @classmethod
    def from_env(cls) -> 'Config':
        load_dotenv()

        config = cls()
        config.discord_token = os.getenv('DISCORD_TOKEN', '')
        config.straico_api_key = os.getenv('STRAICO_API_KEY', '')
        config.command_prefix = os.getenv('COMMAND_PREFIX', '!')
        config.log_level = os.getenv('LOG_LEVEL', 'INFO')
        config.log_file = os.getenv('LOG_FILE')

        try:
            config.max_history_per_channel = int(os.getenv('MAX_HISTORY_PER_CHANNEL', '50'))
            config.max_message_length = int(os.getenv('MAX_MESSAGE_LENGTH', '2000'))
        except ValueError as e:
            raise ConfigurationError(f"Invalid numeric configuration: {e}")

        config.default_chat_model = os.getenv('DEFAULT_CHAT_MODEL', 'openai/gpt-5')
        config.api_base_url = os.getenv('API_BASE_URL', 'https://api.straico.com')

        if not config.discord_token:
            raise ConfigurationError("DISCORD_TOKEN is required")
        if not config.straico_api_key:
            raise ConfigurationError("STRAICO_API_KEY is required")

        return config

    def validate(self) -> None:
        if not self.discord_token:
            raise ConfigurationError("Discord token is required")
        if not self.straico_api_key:
            raise ConfigurationError("Straico API key is required")
        if self.max_history_per_channel < 1:
            raise ConfigurationError("Max history per channel must be positive")
        if self.max_message_length < 100:
            raise ConfigurationError("Max message length must be at least 100")