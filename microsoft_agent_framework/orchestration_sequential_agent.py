import asyncio
from agent_framework import Role
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from agent_framework import SequentialBuilder

async def main() -> None:
    # 1) Create agents using AzureOpenAIChatClient
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())
    
    writer = chat_client.create_agent(
        instructions=(
            "You are a concise copywriter. Provide a single, punchy marketing sentence based on the prompt."
        ),
        name="writer",
    )

    reviewer = chat_client.create_agent(
        instructions=(
            "You are a thoughtful reviewer. Give brief feedback on the previous assistant message."
        ),
        name="reviewer",
    )

    # 2) Build sequential workflow: writer -> reviewer
    workflow = SequentialBuilder().participants([writer, reviewer]).build()

    from agent_framework import ChatMessage, WorkflowOutputEvent

    # 3) Run and print final conversation
    output_evt: WorkflowOutputEvent | None = None
    async for event in workflow.run_stream("Write a tagline for a budget-friendly eBike."):
        if isinstance(event, WorkflowOutputEvent):
            output_evt = event

    if output_evt:
        print("===== Final Conversation =====")
        messages: list[ChatMessage] | Any = output_evt.data
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")

if __name__ == "__main__":
    asyncio.run(main())