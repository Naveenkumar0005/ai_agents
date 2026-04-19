import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# =========================
# Inventory (State)
# =========================
inventory = {
    "niacinamide serum": 0,
    "vitamin c serum": 5,
    "retinol cream": 2
}

restock_requests = {}

# =========================
# Tools (Functions)
# =========================
def check_inventory(product: str):
    product = product.lower()
    stock = inventory.get(product)

    if stock is None:
        return {"status": "not_found"}

    elif stock == 0:
        return {"status": "out_of_stock"}

    return {"status": "in_stock", "quantity": stock}


def request_notification(product: str, customer: str):
    if product not in restock_requests:
        restock_requests[product] = []

    restock_requests[product].append(customer)

    return {
        "status": "subscribed",
        "product": product,
        "customer": customer
    }

# =========================
# Tool Definitions (for LLM)
# =========================
tools = [
    {
        "type": "function",
        "function": {
            "name": "check_inventory",
            "description": "Check if a product is in stock",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {
                        "type": "string",
                        "description": "Product name"
                    }
                },
                "required": ["product"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "request_notification",
            "description": "Subscribe user for restock notification",
            "parameters": {
                "type": "object",
                "properties": {
                    "product": {"type": "string"},
                    "customer": {"type": "string"}
                },
                "required": ["product", "customer"]
            }
        }
    }
]

# =========================
# Tool Execution Router
# =========================
def execute_tool(name, args):
    if name == "check_inventory":
        return check_inventory(**args)

    elif name == "request_notification":
        return request_notification(**args)

    return {"error": "Unknown tool"}

# =========================
# Agent Loop
# =========================
def run_agent(user_input, customer_name):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a smart retail assistant.\n"
                "You can check inventory and subscribe users for restock.\n"
                "Always use tools when needed.\n"
                "Be helpful and concise."
            )
        },
        {"role": "user", "content": user_input}
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
            tools=tools
        )

        message = response.choices[0].message

        #  If LLM wants to call a tool
        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if tool_name == "request_notification":
                    args["customer"] = customer_name

                result = execute_tool(tool_name, args)

                # add tool result back to conversation
                messages.append(message)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

        else:
            return message.content

# =========================
# main Demo 
# =========================
def main():
    print("\n=== Agentic Retail Assistant ===")

    user_queries = [
        "Do you have niacinamide serum?",
        "Okay notify me when it's available"
    ]

    customer = "Naveen"

    for q in user_queries:
        print(f"\nUser: {q}")
        response = run_agent(q, customer)
        print(f"Agent: {response}")


if __name__ == "__main__":
    main()