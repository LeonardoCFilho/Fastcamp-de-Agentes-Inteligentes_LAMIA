from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json

# Agente em si
debt_agent = Agent(
    name="debt_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"), # Alterado de gpt para groq pois nao tenho chave gpt
    description="Suggests a strategy to pay off debt based on income and expenses.",
    instruction=(
        "Given a monthly income, fixed expenses, and total debt, suggest a clear debt payoff strategy. "
        "For each strategy, provide a name, monthly payment amount, and estimated months to pay off. "
        "Respond in JSON format using the key 'debt' with a list of strategy objects." # Alterando para ja ser json aqui
    ) # Estratégias como snowball e avalanche são bem conhecidas, mas o tempo estimado varia com juros
)

# Sessão do agente
session_service = InMemorySessionService()
runner = Runner(
    agent=debt_agent,
    app_name="debt_app",
    session_service=session_service
)
USER_ID = "user_debt"
SESSION_ID = "session_debt"

# Executar
async def execute(request):
    await session_service.create_session( # Adicionando await para garantir o funcionamento
        app_name="debt_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"Monthly income: {request['income']}. Fixed expenses: {request['expenses']}. Total debt: {request['debt']}. "
        f"Suggest 2-3 debt payoff strategies. "
        f"Respond only in JSON with key 'debt' containing a list of objects with 'strategy', 'monthly_payment', and 'estimated_payoff_months'."
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
                if "debt" in parsed and isinstance(parsed["debt"], list):
                    return {"debt": parsed["debt"]}
                else:
                    print("'debt' key missing or not a list in response JSON")
                    return {"debt": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"debt": response_text}  # fallback to raw text