from langchain.agents import initialize_agent, AgentType
from langchain_service.tools.vscode_tools import *
from core.config import EMBEDDING_API
tools = vs_code_tools

llm = ChatOpenAI(model="gpt-4o", temperature=0.7, openai_api_key=EMBEDDING_API)

agent = initialize_agent(tools, llm, agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION, verbose=True)


def handle_user_command():
    while True:
        user_input = input("Enter your command (or type 'exit' to quit): ")

        if user_input.lower() == "exit":
            print("Exiting the agent...")
            break

        # 에이전트로 명령을 전달하고 응답 받기
        response = agent.run(user_input)
        print("Agent response:", response)


# 실시간 명령 처리 시작
if __name__ == "__main__":
    handle_user_command()
