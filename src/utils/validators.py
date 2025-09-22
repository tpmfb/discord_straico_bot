from typing import Optional, List
try:
    from config.models import STRAICO_MODELS, STRAICO_IMAGE_MODELS
    from core.errors import ValidationError
except ImportError:
    # Fallback for when running as standalone module
    import sys
    from pathlib import Path
    src_path = Path(__file__).parent.parent
    sys.path.insert(0, str(src_path))
    from config.models import STRAICO_MODELS, STRAICO_IMAGE_MODELS
    from core.errors import ValidationError


def validate_model(model_name: str, model_list: List[str] = None) -> str:
    if model_list is None:
        model_list = STRAICO_MODELS

    if not model_name:
        raise ValidationError("Model name cannot be empty")

    if model_name not in model_list:
        similar = [m for m in model_list if model_name.lower() in m.lower()]
        if similar:
            raise ValidationError(f"Model '{model_name}' not found. Did you mean: {', '.join(similar[:3])}?")
        else:
            raise ValidationError(f"Model '{model_name}' not found")

    return model_name


def validate_prompt(prompt: str, min_length: int = 1, max_length: int = 1000) -> str:
    if not prompt or not prompt.strip():
        raise ValidationError("Prompt cannot be empty")

    prompt = prompt.strip()

    if len(prompt) < min_length:
        raise ValidationError(f"Prompt must be at least {min_length} characters long")

    if len(prompt) > max_length:
        raise ValidationError(f"Prompt must be no more than {max_length} characters long")

    return prompt


def validate_image_model(model_name: str) -> str:
    return validate_model(model_name, STRAICO_IMAGE_MODELS)


def validate_variations(variations: int) -> int:
    if not isinstance(variations, int) or variations < 1 or variations > 4:
        raise ValidationError("Variations must be between 1 and 4")
    return variations


def validate_aspect_ratio(aspect_ratio: str) -> str:
    valid_ratios = ['square', 'portrait', 'landscape']
    if aspect_ratio not in valid_ratios:
        raise ValidationError(f"Aspect ratio must be one of: {', '.join(valid_ratios)}")
    return aspect_ratio