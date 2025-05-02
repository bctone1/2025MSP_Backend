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

