from langchain_service.chains.qa_chain import get_qa_chain


def test_qa_chain():
    session_id = "test_user_session"  # 예시로 세션 ID 설정
    collection_name = "documents"  # 문서가 저장된 컬렉션 이름
    provider = "openai"  # OpenAI 모델 사용
    model = "gpt-3.5-turbo"  # 사용할 모델 지정 (선택사항)

    # QA 체인 생성
    qa_chain = get_qa_chain(session_id, collection_name, provider, model)

    # QA 체인 타입 확인
    print("QA 체인 타입:", type(qa_chain))

    # 사용자 질문 예시
    question = "프로젝트의 데이터베이스 구조는 어떻게 되나요?"

    # 질문에 대한 응답 실행
    try:
        # invoke() 메서드를 사용하여 질문을 처리
        result = qa_chain.invoke({"question": question})

        # 'answer' 출력만 반환하도록 설정
        answer = result.get('answer', 'No answer found')
        print("답변:", answer)

        # 출처 문서도 확인 (선택사항)
        source_documents = result.get('source_documents', '출처 문서 없음')
        print("출처 문서:", source_documents)
    except Exception as e:
        print("에러 발생:", e)


# 테스트 실행
test_qa_chain()
