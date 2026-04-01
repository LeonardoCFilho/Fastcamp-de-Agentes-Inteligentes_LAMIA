from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

# Agente em si
budget_agent = Agent(
    name="budget_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"), # Alterado de gpt para groq pois nao tenho chave gpt
    description="Analyzes income and expenses and suggests a monthly budget breakdown.",
    instruction=(
        "Given a monthly income and fixed expenses, suggest a detailed monthly budget. "
        "Break it down into categories like housing, food, transport, leisure, and savings. "
        "For each category, provide a name, suggested amount, and a practical tip. "
        "Respond in JSON format using the key 'budget' with a list of category objects."
    ) # As sugestões de valor por categoria dependem muito do estilo de vida, mas servem como ponto de partida
)

# Sessão do agente
session_service = InMemorySessionService()
runner = Runner(
    agent=budget_agent,
    app_name="budget_app",
    session_service=session_service
)
USER_ID = "user_budget"
SESSION_ID = "session_budget"

# Executar
async def execute(request):
    await session_service.create_session( # Adicionando await para garantir o funcionamento
        app_name="budget_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Monthly income: {request['income']}. Fixed expenses: {request['expenses']}. "
        f"Suggest a monthly budget broken into categories. "
        f"Respond only in JSON with key 'budget' containing a list of objects with 'category', 'suggested_amount', and 'tip'."
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
                if "budget" in parsed and isinstance(parsed["budget"], list):
                    return {"budget": parsed["budget"]}
                else:
                    print("'budget' key missing or not a list in response JSON")
                    return {"budget": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"budget": response_text}  # fallback to raw text
