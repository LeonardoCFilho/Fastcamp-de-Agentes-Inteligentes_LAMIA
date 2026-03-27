from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool
from google.adk.models.lite_llm import LiteLlm


from .sub_agents.recipe_chef.agent import recipe_chef
from .sub_agents.fitness_coach.agent import fitness_coach
from .tools.tools import get_current_time

root_agent = Agent(
    name="manager",
    model=LiteLlm(model="groq/llama-3.3-70b-versatile"),
    description="Manager agent",
    instruction="""
    You are a manager agent responsible for overseeing and delegating tasks.

    You have the following sub-agent — delegate conversations directly to it:
    - fitness_coach: handles workout routines, training plans, and fitness goals

    You have the following tools — call them directly when needed and use the result in your response:
    - recipe_chef: call this tool to get recipe suggestions and cooking guidance
    - get_current_time: returns the current date and time

    Routing guide:
    - Anything about exercise, training, or fitness goals → delegate to fitness_coach
    - Anything about food, recipes, or cooking → call the recipe_chef tool and return the result
    - Combined topics (e.g. post-workout meal) → call recipe_chef tool first, then delegate to fitness_coach

    Never answer culinary or fitness questions yourself. Always use the appropriate agent or tool.
    """,
    # Uma coisa interessante é que devido o modo que news_analyst precisa ser implementado AgentTool o agente líder tem sua prompt alterada
    sub_agents=[fitness_coach],
    tools=[
        AgentTool(recipe_chef),
        get_current_time,
    ],
)
