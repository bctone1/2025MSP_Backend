def estimate_claude_cost(model: str, prompt_tokens: int, completion_tokens: int):
    prices = {
        "claude-3-haiku-20240307": (0.00025, 0.00125),
        "claude-3-sonnet-20240229": (0.003, 0.015),
        "claude-3-opus-20240229": (0.015, 0.075),
    }

    prompt_price, completion_price = prices.get(model, (0.0, 0.0))
    cost = (prompt_tokens * prompt_price + completion_tokens * completion_price) / 1000

    return {
        "prompt": prompt_tokens,
        "completion": completion_tokens,
        "total": prompt_tokens + completion_tokens,
        "cost": round(cost, 6)
    }

def count_tokens(text: str):
    return int(len(text) / 4)