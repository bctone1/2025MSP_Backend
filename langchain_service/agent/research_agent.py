from core.config import SEARCH_API
from langchain_service.llm.setup import get_llm
from typing import List
from serpapi import GoogleSearch
import ast
import re

# 검색하기 전, LLM이 질문을 파악하고 핵심 검색 키워드를 선별함
def select_keyword(provider : str, model : str, api_key : str, message : str):
    llm = get_llm(provider = provider, model = model, api_key = api_key, temperature = 0.1)
    prompt = f"""
    사용자 질문에 대한 답변을 위해, 검색을 통하여 정보를 조사할 예정입니다.
    Google 검색 기준으로 가장 효과적인 검색 키워드를 추천해주세요.
    질문: {message}
    
    답변 생성 시 다른 부가적인 설명이나 불필요한 텍스트 없이,  
    키워드만 차례대로 하나씩 출력해주세요.
    **답변 예시의 양식을 반드시 지켜서 출력해주세요.**
    **키워드는 핵심 키워드 3개만 추출해주세요.**
    **검색 키워드는 해당 키워드로 검색 시 충분히 질문에 대한 답변이 될만한 것들로 선별해주세요.** 
    
    답변 예시:
    [키워드 1, 키워드 2, 키워드 3]
    """
    response = llm.invoke(prompt)
    return response.content

# LLM이 생성한 키워드 리스트가 유효한지 검증 -> 실패하면 false 반환
def is_valid_keyword_format(response_text: str) -> bool:
    match = re.search(r"\[([^][]*,[^][]*)]", response_text)
    return bool(match)

# LLM이 생성한 키워드 리스트를 파이썬에서 처리 가능한 리스트로 파싱
def extract_keywords(response_text: str) -> List[str]:
    list_str = re.search(r"\[[^][]*]", response_text).group()

    try:
        # 따옴표가 있다면 그대로 ast.literal_eval로 처리
        return ast.literal_eval(list_str)
    except (SyntaxError, ValueError):
        # 따옴표 없으면 수동으로 split하여 문자열 리스트로 변환
        inner = list_str[1:-1]  # 대괄호 제거
        items = [item.strip() for item in inner.split(",") if item.strip()]
        return items

# 검색 엔진
def search_engine(keywords, api_key, max_results_per_keyword=3):
    all_results = {}
    for keyword in keywords:
        params = {
            "engine": "google",
            "q": keyword,
            "api_key": api_key,
            "num": max_results_per_keyword
        }
        search = GoogleSearch(params)
        results = search.get_dict()

        items = []
        for item in results.get("organic_results", []):
            items.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "snippet": item.get("snippet")
            })
        all_results[keyword] = items[:max_results_per_keyword]

    return all_results

def build_text_for_ai(all_results: dict) -> str:
    texts = []
    for keyword, items in all_results.items():
        if not items:
            continue
        texts.append(f"키워드: {keyword}\n")
        for idx, item in enumerate(items, 1):
            title = item.get("title", "").strip()
            snippet = item.get("snippet", "").strip()
            if title and snippet:
                texts.append(f"{idx}. {title}\n{snippet}\n")
        texts.append("\n")
    return "\n".join(texts)

# 최종 결과 생성
def generate_result(provider: str, model: str, api_key: str, message: str, search_result : str):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.7)
    prompt = f"""
    사용자가 질문을 했습니다.
    
    사용자 질문 내용 : {message}
    
    사용자 질문에 대한 답변을 주세요.
    **답변은 최대한 구체적으로, 잘 정리된 구조로 생성해주세요.**
    
    아래 내용들은 답변 생성을 위해 참고할 수 있는 자료입니다.
    기존의 가지고 있던 데이터와 참고 자료들의 내용들을 잘 결합한 결과를 생성해주세요.  
    **만약 참고 자료가 답변 생성에 불필요하다고 판단되면, 참고 자료 내용을 무시하고 답변을 생성해도 좋습니다.**
    
    # 해당 질문 관련 Google 검색 결과
    {search_result}
    """
    response = llm.invoke(prompt)
    return response.content

# 일반 LLM 답변 ( 리서치 에이전트와 성능 비교하기 위함 )
def generate_result_normal(provider: str, model: str, api_key: str, message: str):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.7)
    prompt = f"""
    사용자가 질문을 했습니다.

    사용자 질문 내용 : {message}

    사용자 질문에 대한 답변을 주세요.

    아래 내용들은 답변 생성을 위해 참고할 수 있는 자료입니다.

    **답변은 최대한 구체적으로, 잘 정리된 구조로 생성해주세요.**

    """
    response = llm.invoke(prompt)
    return response.content


# 함수들을 차례대로 수행하고 결과를 반환하는 에이전트
def research_agent(provider: str, model: str, api_key: str, message: str):
    max_attempts = 3 # 유효성 검사 최대 반복 횟수
    keyword_list = None
    # 유효성 검사를 통과하면 데이터를 사용
    for attempt in range(max_attempts):
        keyword_list_raw = select_keyword(provider, model, api_key, message)
        if is_valid_keyword_format(keyword_list_raw):
            keyword_list = keyword_list_raw
            break

    if not keyword_list:
        raise ValueError("유효한 키워드 포맷을 생성하지 못했습니다.")

    keywords = extract_keywords(keyword_list)

    get_search = search_engine(keywords, SEARCH_API)

    search_result = build_text_for_ai(get_search)

    response = generate_result(provider, model, api_key, message, search_result)

    return response

