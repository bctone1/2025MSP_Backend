from langchain_service.memory.relevant_message import *
from core.config import EMBEDDING_API

# 사용자 입력 처리 및 목적 파악
def extract_writing_intent(provider, model, api_key, user_prompt):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.2)
    prompt = f"""
    사용자의 요청을 분석하여 글의 목적과 요구사항을 정리해주세요.

    사용자 입력:
    {user_prompt}

    출력 예시:
    - 글의 목적:
    - 주요 키워드:
    - 글의 대상 독자:
    - 톤 & 스타일:
    - 기대 효과:
    """
    response = llm.invoke(prompt)
    return response.content

# 글의 구조 설계
def design_creative_structure(provider, model, api_key, writing_intent):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.4)
    prompt = f"""
    다음 글쓰기 요구사항을 바탕으로 글의 전체 구조를 기획해주세요.
    - 서론, 본론, 결론 등의 구조와, 각 파트에서 다룰 내용을 창의적으로 기획하세요.
    - 예상 소제목과 아이디어도 포함해주세요.

    요구사항:
    {writing_intent}

    출력 예시:
    [글 구성]
    1. 서론: 문제 제기 또는 흥미 유도
    2. 본론1: 핵심 주장
    3. 본론2: 사례 또는 비유
    4. 결론: 정리 및 독자에게 남기는 메시지

    [아이디어]
    - 비유: ...
    - 질문 유도: ...
    """
    response = llm.invoke(prompt)
    return response.content

# 본문 생성
def generate_structured_article(provider, model, api_key, structure_plan):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.7)
    prompt = f"""
    아래의 글 구조와 아이디어를 바탕으로 전체 글을 작성해주세요.
    - 글은 서론, 본론, 결론 순으로 구성되며, 문체는 일관되고 자연스럽게 유지해주세요.
    - 독창적인 비유, 사례, 메시지를 포함하여 읽는 이에게 인상을 남기도록 하세요.

    # 글 구조 및 아이디어
    {structure_plan}

    **글을 전체적으로 하나의 흐름으로 작성해주세요.**
    """
    response = llm.invoke(prompt)
    return response.content

# 품질 검사 및 개선 피드백 생성
def evaluate_creative_quality(provider, model, api_key, article):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.3)
    prompt = f"""
    다음 글의 품질을 평가하고 개선할 부분을 간단히 정리해주세요.

    - 문체 일관성
    - 논리적 흐름
    - 창의성/독창성
    - 대상 독자 적합성

    글:
    {article}

    출력 예시:
    - 장점: ...
    - 개선 제안: ...
    """
    response = llm.invoke(prompt)
    return response.content

# 최종 에이전트
def creative_writing_agent(provider, model, api_key, user_prompt):
    writing_intent = extract_writing_intent(provider, model, api_key, user_prompt)
    structure_plan = design_creative_structure(provider, model, api_key, writing_intent)
    article = generate_structured_article(provider, model, api_key, structure_plan)
    quality_review = evaluate_creative_quality(provider, model, api_key, article)

    return {
        "요구사항 정리": writing_intent,
        "글 구조 및 아이디어": structure_plan,
        "생성된 글": article,
        "품질 평가": quality_review
    }

prompt = "인공지능이 예술 창작에 미치는 긍정적 영향에 대해 창의적인 시각으로 글을 써줘"
answer = creative_writing_agent("openai", "gpt-4o", EMBEDDING_API, prompt)