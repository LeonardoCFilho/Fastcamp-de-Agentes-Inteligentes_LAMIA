from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# Agente em si
host_agent = Agent(
    name="host_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"), # Alterado de gpt para groq pois nao tenho chave gpt
    description="Coordinates personal finance planning by calling budget, savings, and debt agents.",
    instruction="You are the host agent responsible for orchestrating personal finance tasks. "
                "You call external agents to gather budget analysis, savings recommendations, and debt strategies, then return a final result."
)
# Essa implementação é interessante, o agente não 'sabe' diretamente dos outros agentes, é mencionado a existencia, mas não é dado em sub_agents
# Isso funciona ja que os 3 agentes sempre estão online, podendo conversar de modo independente, isso permitiria mais de um host conversar com o mesmo agente

# Sessão do agente
session_service = InMemorySessionService()
runner = Runner(
    agent=host_agent,
    app_name="host_app",
    session_service=session_service
)
USER_ID = "user_host"
SESSION_ID = "session_host"

# Executar
async def execute(request):
    await session_service.create_session( # Adicionando await para garantir o funcionamento
        app_name="host_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Create a personal finance plan for someone with a monthly income of {request['income']}, "
        f"fixed expenses of {request['expenses']}, and total debt of {request['debt']}. "
        f"Call the budget, savings, and debt agents for results."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            return {"summary": event.content.parts[0].text}
