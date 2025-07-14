from langchain_service.memory.relevant_message import *
from langchain_service.embedding.get_vector import text_to_vector
from sqlalchemy.orm import Session

# DB 내의 대화 이력 RAG 기반 검색
def get_session_log(db : Session, user_email : str, message : str):
    embedding_message = text_to_vector(message)
    session_log = get_session_log_by_user_info(db = db, user_email = user_email, embedding_message= embedding_message)
    return session_log

# 전체적인 대화 흐름 기반으로 요구사항 정리
def make_requirements(provider: str, model: str, api_key: str, message: str, session_logs : str):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.7)
    prompt = f"""
        사용자의 질문을 바탕으로 요구사항을 정리해주세요.
        
        사용자 질문 : {message}
        
        아래 내용들은 기존에 사용자가 AI 모델과 주고 받았던 대화 기록의 일부입니다. 
        만약 요구사항을 정의하기 위해 필요한 데이터라고 판단되면 참고하고, 
        그렇지 않다고 판단되면 무시하세요.
        
        **사용자가 따로 선택한 프로그래밍 언어가 없을 시, Python을 기준으로 요구사항을 작성해주세요.**
        
        # 기존 대화 이력
        {session_logs}
        """
    response = llm.invoke(prompt)
    return response.content

# 요구사항에 따라 코드 생성
def generate_main_code(provider: str, model: str, api_key: str, requirements : str):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.9)
    prompt = f"""
        현재 프로젝트의 요구사항입니다. 
        이 요구 사항들을 충족시키는 코드를 작성해주세요.
        **코드의 일부분만 출력하는 것이 아닌, 전체 코드를 출력해야 합니다.**
        **해당 코드를 바로 실행해도 동작하게끔, 코드에 생략되는 부분이 없도록 합니다.**
        **다른 설명없이, 오로지 코드만 출력해주세요.**
        
        # 요구사항
        {requirements}
        """
    response = llm.invoke(prompt)
    return response.content

# 코드에 문제가 없는지 검증
def error_test(requirements : str, code : str, provider : str, model : str, api_key : str):
    llm = get_llm(provider=provider, model=model, api_key=api_key, temperature=0.1)
    prompt = f"""
            요구사항을 기준으로 코드를 작성했습니다.
            요구사항과 작성된 코드를 비교하여,
            코드가 제대로 작성되었는지 아닌지 체크해주세요.
            
            **답변은 항상 추가적인 설명 없이, 숫자로 번호만 알려주세요.**
            1. 코드에 문제가 없음
            2. 문법적인 오류가 존재함
            3. 문법적으로는 정상적이지만, 요구사항과 관련이 없는 코드임.
            
            **1, 2, 3 중 하나의 숫자만 출력해주세요.**
            
            # 요구사항
            {requirements}

            # 작성된 코드
            {code}
            """
    response = llm.invoke(prompt)
    return response.content



# 함수들을 차례대로 수행하고 결과를 반환하는 에이전트
def code_agent(db : Session, user_email : str, provider : str, model : str, api_key : str, message : str):
    session_log = get_session_log(db = db, user_email = user_email, message = message)
    requirements = make_requirements(provider = provider, api_key = api_key, model = model,
                                     message = message, session_logs = session_log)
    main_code = generate_main_code(provider = provider, model = model, api_key = api_key, requirements = requirements)
    error_test_result = error_test(requirements = requirements, code = main_code,
                                   provider = provider, model = model, api_key = api_key)
    print(main_code)
    return {
        "요구사항 " : requirements,
        "생성된 코드" : main_code,
        "에러 테스트" : error_test_result
    }

