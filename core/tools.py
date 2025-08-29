from core.config import CLAUDE_MODELS


def fit_anthropic_model(model_name : str):
    if model_name == 'claude-3-opus':
        return CLAUDE_MODELS[0]
    if model_name == 'claude-3-sonnect':
        return CLAUDE_MODELS[1]
    if model_name == 'claude-3-haiku':
        return CLAUDE_MODELS[2]
    if model_name == 'claude-3.5-haiku':
        return CLAUDE_MODELS[3]
    if model_name == 'claude-4-opus':
        return CLAUDE_MODELS[4]
    if model_name == 'claude-4-sonnet':
        return CLAUDE_MODELS[5]
    else:
        return model_name


def mask_api_key(api_key: str) -> str:
    if not isinstance(api_key, str):
        raise ValueError("API 키는 문자열이어야 합니다.")

    if not api_key.startswith("sk-"):
        return "*" * len(api_key)

    prefix = "sk-"
    key_body = api_key[len(prefix):]

    if len(key_body) <= 4:
        masked = "*" * len(key_body)
        return prefix + masked

    num_visible = 4
    masked_body = "*" * (len(key_body) - num_visible) + key_body[-num_visible:]
    return prefix + masked_body


def FRIENDLI_AI(model_name : str):
    if model_name == 'exaone-3.5':
        return FRIENDLI_AI[0]
    else:
        return model_name

