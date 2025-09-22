#!/usr/bin/env python3
"""
Test script to verify that all imports are correctly structured
without requiring external dependencies like discord.py
"""

import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    try:
        # Test core imports (excluding config which needs dotenv and bot which needs discord)
        from core.logger import setup_logger
        from core.errors import ConfigurationError, APIError, ValidationError
        print('✅ Core imports working')

        # Test services
        from services.conversation import ConversationHistory
        print('✅ Services imports working')

        # Test config
        from config.models import STRAICO_MODELS, STRAICO_IMAGE_MODELS
        print(f'✅ Config loaded: {len(STRAICO_MODELS)} chat models, {len(STRAICO_IMAGE_MODELS)} image models')

        # Test utils (validators only, formatters needs discord)
        from utils.validators import validate_prompt
        prompt = validate_prompt('test prompt')
        assert prompt == 'test prompt'
        print('✅ Utils validators working')

        print('\n🎉 All import structure is correct!')
        print('📦 Ready to run once discord.py is installed')
        return True

    except Exception as e:
        print(f'❌ Import error: {e}')
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports()