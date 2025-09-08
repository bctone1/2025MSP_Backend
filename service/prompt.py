import json
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from core.config import   OPENAI_API
from langchain_community.chat_models import ChatOpenAI
from core.config import  DEFAULT_CHAT_MODEL


def preview_prompt(input : str,):
    llm = ChatOpenAI(
        model_name=DEFAULT_CHAT_MODEL,
        temperature=0,
        streaming=False,
        openai_api_key=OPENAI_API
    )

    template = """
        다음은 사용자가 보낸 요청입니다:
        "{input}"
        위 내용을 요약해서 아래 JSON 형식으로만 답변하세요:
        {{
            "title": "...",
            "preview": "..."
        }}
        """

    prompt = PromptTemplate(
        input_variables=["input"],
        template=template
    )
    chain = LLMChain(llm=llm, prompt=prompt)
    response = chain.invoke({"input": input})
    # return response
    text_output = response["text"]

    try:
        # JSON 문자열 파싱
        parsed = json.loads(text_output)
        return parsed
    except json.JSONDecodeError:
        # JSON이 아닐 경우 fallback 처리
        return {"title": None, "preview": text_output}

