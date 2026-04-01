from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
import json


flight_agent = Agent(
    name="flight_agent",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"), # Alterado de gpt para groq pois nao tenho chave gpt
    description="Suggests the best flights to the user's destination.",
    instruction=(
        "Given a destination, dates, and budget, suggest 2-3 flights to that location. "
        "For each flight, provide the company's name, price estimate, departure time and flight details. "
        "Respond in plain English. Keep it concise and well-formatted."
    )
)
# Confirmei a resposta depois essas empresas realmente existem, interessante ver que ate isso caiu no treinamento da IA

session_service = InMemorySessionService()
runner = Runner(
    agent=flight_agent,
    app_name="flight_app",
    session_service=session_service
)
USER_ID = "user_flights"
SESSION_ID = "session_flights"

async def execute(request):
    await session_service.create_session( # Adicionando await para garantir o funcionamento
        app_name="flight_app",
        user_id=USER_ID,
        session_id=SESSION_ID
    )
    prompt = (
        f"User is flying to {request['destination']} from {request['start_date']} to {request['end_date']}, "
        f"with a budget of {request['budget']}. Suggest 2-3 flight options, each with company's name, price estimate, departure time and flight details. "
        f"Respond in JSON format using the key 'flights' with a list of flights objects." # As IAs obedeceram muita bem a saida desejada
    )
    message = types.Content(role="user", parts=[types.Part(text=prompt)])
    async for event in runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=message):
        if event.is_final_response():
            response_text = event.content.parts[0].text
            try:
                parsed = json.loads(response_text)
                if "flights" in parsed and isinstance(parsed["flights"], list):
                    return {"flights": parsed["flights"]}
                else:
                    print("'flights' key missing or not a list in response JSON")
                    return {"flights": response_text}  # fallback to raw text
            except json.JSONDecodeError as e:
                print("JSON parsing failed:", e)
                print("Response content:", response_text)
                return {"flights": response_text}  # fallback to raw text