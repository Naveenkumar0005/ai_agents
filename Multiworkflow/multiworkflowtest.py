
import os
import asyncio
from typing import Dict
from openai import AsyncOpenAI
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, trace,OpenAIChatCompletionsModel, input_guardrail, GuardrailFunctionOutput
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from pydantic import BaseModel


load_dotenv(override=True)

# -----------------------------
# 1. SALES AGENTS (Email writers)
# -----------------------------

instructions1 = "You are a sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write professional, serious cold emails."

instructions2 = "You are a humorous, engaging sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write witty, engaging cold emails that are likely to get a response."

instructions3 = "You are a busy sales agent working for ComplAI, \
a company that provides a SaaS tool for ensuring SOC2 compliance and preparing for audits, powered by AI. \
You write concise, to the point cold emails."



# 1. Create a DeepSeek client pointing to DeepSeek's API endpoint
deepseek_client = AsyncOpenAI(
    base_url="https://api.deepseek.com/v1",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
)
# 2. Wrap it in OpenAIChatCompletionsModel
deepseek_model = OpenAIChatCompletionsModel(
    model="deepseek-chat",
    openai_client=deepseek_client,
)

sales_agent1 = Agent(
    name="Professional Sales Agent",
    instructions=instructions1,
    model=deepseek_model
)

sales_agent2 = Agent(
    name="Engaging Sales Agent",
    instructions=instructions2,
    model=deepseek_model
)

sales_agent3 = Agent(
    name="Busy Sales Agent",
    instructions=instructions3,
    model=deepseek_model
)


# Convert agents to tools
sales_tool1 = sales_agent1.as_tool(
    tool_name="sales_agent1",
    tool_description="Generate a professional cold email"
)

sales_tool2 = sales_agent2.as_tool(
    tool_name="sales_agent2",
    tool_description="Generate an engaging cold email"
)

sales_tool3 = sales_agent3.as_tool(
    tool_name="sales_agent3",
    tool_description="Generate a concise cold email"
)


# -----------------------------
# 2. SUBJECT + HTML AGENTS
# -----------------------------

subject_instructions = "You can write a subject for a cold sales email. \
You are given a message and you need to write a subject for an email that is likely to get a response."

html_instructions = "You can convert a text email body to an HTML email body. \
You are given a text email body which might have some markdown \
and you need to convert it to an HTML email body with simple, clear, compelling layout and design."

subject_writer = Agent(name="Email subject writer", instructions=subject_instructions, model=deepseek_model)
subject_tool = subject_writer.as_tool(tool_name="subject_writer", tool_description="Write a subject for a cold sales email")

html_converter = Agent(name="HTML email body converter", instructions=html_instructions, model=deepseek_model)
html_tool = html_converter.as_tool(tool_name="html_converter",tool_description="Convert a text email body to an HTML email body")


# -----------------------------
# 3. SEND EMAIL TOOL
# -----------------------------

@function_tool
async def send_html_email(subject: str, html_body: str) -> Dict[str, str]:
    """Send email using SendGrid"""

    sg = sendgrid.SendGridAPIClient(
        api_key=os.environ.get("SENDGRID_API_KEY")
    )

    from_email = Email("btc.comviva@gmail.com")
    to_email = To("naveennita07@gmail.com")

    content = Content("text/html", html_body)

    mail = Mail(from_email, to_email, subject, content).get()

    try:
        response = sg.client.mail.send.post(request_body=mail)
        return {"status": "sent", "code": response.status_code}
    except Exception as e:
        return {"status": "error", "message": str(e)}


# -----------------------------
# 4. EMAIL MANAGER AGENT
# -----------------------------

emailer_agent = Agent(
    name="Email Manager",
    instructions=""" You MUST follow these steps strictly:
    1. Use subject_writer tool to generate subject
    2. Use html_converter tool to convert body to HTML
    3. Use send_html_email tool to send email
    Do not skip any step. """,
    tools=[subject_tool, html_tool, send_html_email],
    model=deepseek_model,
    handoff_description="Formats and sends email")

# -----------------------------
# 5. SALES MANAGER AGENT
# -----------------------------

sales_manager = Agent(
    name="Sales Manager",
    instructions="""
1. Use tools:
   - sales_agent1
   - sales_agent2
   - sales_agent3
   to generate drafts
2. Pick the best one
3. Send ONLY that email to Email Manager
""",
    tools=[sales_tool1, sales_tool2, sales_tool3],
    handoffs=[emailer_agent],
    model=deepseek_model
)

class NameCheckOutput(BaseModel):
    is_name_in_message: bool
    name: str

guardrail_agent = Agent( 
    name="Name check",
    instructions="Check if the user is including someone's personal name in what they want you to do.",
    output_type=NameCheckOutput,
    model=deepseek_model
)

@input_guardrail
async def guardrail_against_name(ctx, agent, message):
    result = await Runner.run(guardrail_agent, message, context=ctx.context)
    is_name_in_message = result.final_output.is_name_in_message
    return GuardrailFunctionOutput(output_info={"found_name": result.final_output},tripwire_triggered=is_name_in_message)

careful_sales_manager = Agent(
    name="Sales Manager",
    instructions="""
    1. Use tools:
    - sales_agent1
    - sales_agent2
    - sales_agent3
    to generate drafts
    2. Pick the best one
    3. Send ONLY that email to Email Manager """,
    tools=[sales_tool1, sales_tool2, sales_tool3],
    handoffs=[emailer_agent],
    model=deepseek_model,
    input_guardrails=[guardrail_against_name]
    )
    
# -----------------------------
# 6. MAIN EXECUTION
# -----------------------------

async def main():
    print("Running Sales Manager...")
    message = "Write a cold sales email to a CEO from Naveen about SOC2 compliance SaaS"

    with trace("Automated SDR Pipeline"):
        result = await Runner.run(careful_sales_manager, message)

    print("\n✅ FINAL RESULT:\n")
    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())

