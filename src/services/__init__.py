# Services module - import on demand to avoid dependency issues

__all__ = ['StraicoService', 'ConversationHistory']

def get_straico_service():
    from .straico import StraicoService
    return StraicoService

def get_conversation_history():
    from .conversation import ConversationHistory
    return ConversationHistory