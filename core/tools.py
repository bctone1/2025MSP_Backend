from core.config import CLAUDE_MODELS

def fit_anthropic_model(model_name : str):
    if model_name == 'claude-3-opus':
        return CLAUDE_MODELS[0]
    if model_name == 'claude-3-sonnect':
        return CLAUDE_MODELS[1]
    if model_name == 'claude-3-haiku':
        return CLAUDE_MODELS[2]
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