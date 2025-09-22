class BotError(Exception):
    pass

class APIError(BotError):
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code

class ValidationError(BotError):
    pass

class PluginError(BotError):
    pass

class ConfigurationError(BotError):
    pass