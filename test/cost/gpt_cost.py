import requests
from datetime import datetime, timedelta
import core.config as cp
import openai

OPENAI_API_KEY = cp.GPT_API


def request_gpt(prompt):
    client = openai.OpenAI(api_key=OPENAI_API_KEY)  # 최신 방식 적용
    response = client.chat.completions.create(
        model="gpt-4-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    usage = response.usage
    prompt_tokens = usage.prompt_tokens
    completion_tokens = usage.completion_tokens
    total_tokens = usage.total_tokens

    # OpenAI 비용 계산 (2024년 기준 GPT-4 Turbo)
    cost = (prompt_tokens * 0.01 + completion_tokens * 0.03) / 1000  # 달러($) 기준

    print(f"사용된 비용: ${cost:.4f}")
    return response.choices[0].message.content

# 실행
request_gpt("안녕하세요, 오늘 날씨는 어때?")