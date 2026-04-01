from common.a2a_client import call_agent
BUDGET_URL   = "http://localhost:8001/run"
SAVINGS_URL  = "http://localhost:8002/run"
DEBT_URL     = "http://localhost:8003/run"

async def run(payload):
    #Print what the host agent is sending
    print("Incoming payload:", payload)
    budget = await call_agent(BUDGET_URL,  payload)
    savings = await call_agent(SAVINGS_URL, payload)
    debt = await call_agent(DEBT_URL,    payload)
    # Log outputs
    print("budget:", budget)
    print("savings:", savings)
    print("debt:", debt)
    # Ensure all are dicts before access
    budget = budget if isinstance(budget, dict) else {}
    savings = savings if isinstance(savings, dict) else {}
    debt = debt if isinstance(debt, dict) else {}
    return {
        "budget": budget.get("budget", "No budget analysis returned."),
        "savings": savings.get("savings", "No savings recommendations returned."),
        "debt": debt.get("debt", "No debt strategy returned.")
    }
