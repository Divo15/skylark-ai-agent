from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import anthropic
import json
import os
from dotenv import load_dotenv
from monday_client import get_deals, get_work_orders
from data_cleaner import clean_deals, clean_work_orders
from tools import TOOLS

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

class ChatRequest(BaseModel):
    message: str
    history: list = []

def execute_tool(tool_name: str, tool_input: dict) -> dict:
    trace = {
        "tool": tool_name,
        "input": tool_input,
        "status": "fetching..."
    }

    if tool_name == "get_deals_data":
        raw = get_deals()
        data = clean_deals(raw)

        if tool_input.get("sector"):
            data = [d for d in data if
                    tool_input["sector"].lower() in d["sector"].lower()]
        if tool_input.get("status"):
            data = [d for d in data if
                    tool_input["status"].lower() in d["status"].lower()]

        trace["status"] = f"Retrieved {len(data)} deals from monday.com"
        return {"data": data, "trace": trace}

    elif tool_name == "get_work_orders_data":
        raw = get_work_orders()
        data = clean_work_orders(raw)

        if tool_input.get("sector"):
            data = [d for d in data if
                    tool_input["sector"].lower() in d["sector"].lower()]
        if tool_input.get("status"):
            data = [d for d in data if
                    tool_input["status"].lower() in d["status"].lower()]

        trace["status"] = f"Retrieved {len(data)} work orders from monday.com"
        return {"data": data, "trace": trace}

    elif tool_name == "get_combined_data":
        raw_deals = get_deals()
        raw_wo = get_work_orders()
        deals = clean_deals(raw_deals)
        work_orders = clean_work_orders(raw_wo)

        if tool_input.get("sector"):
            deals = [d for d in deals if
                     tool_input["sector"].lower() in d["sector"].lower()]
            work_orders = [w for w in work_orders if
                           tool_input["sector"].lower() in w["sector"].lower()]

        trace["status"] = f"Retrieved {len(deals)} deals + {len(work_orders)} work orders from monday.com"
        return {
            "deals": deals,
            "work_orders": work_orders,
            "trace": trace
        }

@app.post("/chat")
async def chat(request: ChatRequest):
    messages = request.history + [
        {"role": "user", "content": request.message}
    ]

    tool_traces = []

    system_prompt = """You are a business intelligence assistant for a drone survey company.
You help founders and executives understand their business data from monday.com.

RULES:
- ALWAYS use tools to fetch live data before answering. Never guess numbers.
- When data has nulls or missing values, mention it as a caveat.
- Give concise, insight-focused answers.
- Use Indian number formatting: Lakhs (L) and Crores (Cr) for rupees.
- If someone asks about 'energy sector', there is no exact match - suggest Renewables instead.
- Support follow-up questions using conversation history.
- If a question is ambiguous, ask a clarifying question."""

    response = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1000,
        system=system_prompt,
        tools=TOOLS,
        messages=messages
    )

    while response.stop_reason == "tool_use":
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_traces.append(result.get("trace", {}))

                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(result)
                })

        messages.append({"role": "assistant", "content": response.content})
        messages.append({"role": "user", "content": tool_results})

        response = client.messages.create(
            model="claude-haiku-4-5",
            max_tokens=1000,
            system=system_prompt,
            tools=TOOLS,
            messages=messages
        )

    answer = ""
    for block in response.content:
        if hasattr(block, "text"):
            answer = block.text

    return {
        "answer": answer,
        "tool_traces": tool_traces
    }

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/")
def root():
    return FileResponse("static/index.html")