from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

# Agente em si
savings_agent = Agent(
    name="savings_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"), # Alterado de gpt para groq pois nao tenho chave gpt
    description="Recommends savings goals and simple investment options based on income and expenses.",
    instruction=(
        "Given a monthly income and fixed expenses, recommend savings goals and beginner-friendly investment options. "
        "For each recommendation, provide a goal name, suggested monthly amount, and a rationale. "
        "Respond in JSON format using the key 'savings' with a list of recommendation objects."
    ) # Sugestões de investimento são genéricas — não substituem consultoria financeira profissional
)

# Sessão do agente
session_service = InMemorySessionService()
runner = Runner(
    agent=savings_agent,
    app_name="savings_app",
    session_service=session_service
)
USER_ID = "user_savings"
SESSION_ID = "session_savings"

# Executar
async def execute(request):
    await session_service.create_session( # Adicionando await para garantir o funcionamento
        app_name="savings_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Monthly income: {request['income']}. Fixed expenses: {request['expenses']}. "
        f"Recommend 2-3 savings goals and simple investment options. "
        f"Respond only in JSON with key 'savings' containing a list of objects with 'goal', 'monthly_amount', and 'rationale'."
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            # por retornar json tenho que garantir um padrao
            response_text = response_text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("\n", 1)[-1]
                response_text = response_text.rsplit("```", 1)[0].strip()
            try:
                parsed = json.loads(response_text)
                if "savings" in parsed and isinstance(parsed["savings"], list):
                    return {"savings": parsed["savings"]}
                else:
                    print("'savings' key missing or not a list in response JSON")
                    return {"savings": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"savings": response_text}  # fallback to raw text