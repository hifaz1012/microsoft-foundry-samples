import asyncio
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from agent_framework import ChatAgent, ChatMessage, GroupChatBuilder
from typing import cast
from agent_framework import Role, WorkflowOutputEvent, AgentRunUpdateEvent

# Initialize the Azure OpenAI chat client
chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

async def main() -> None:
    # Create a researcher agent
    researcher = ChatAgent(
        name="Researcher",
        description="Collects relevant background information.",
        instructions="Gather concise facts that help answer the question. Be brief and factual.",
        chat_client=chat_client,
    )

    # Create a writer agent
    writer = ChatAgent(
        name="Writer",
        description="Synthesizes polished answers using gathered information.",
        instructions="Compose clear, structured answers using any notes provided. Be comprehensive.",
        chat_client=chat_client,
    )

    # Create orchestrator agent for speaker selection
    orchestrator_agent = ChatAgent(
        name="Orchestrator",
        description="Coordinates multi-agent collaboration by selecting speakers",
        instructions="""
    You coordinate a team conversation to solve the user's task.

    Guidelines:
    - Start with Researcher to gather information
    - Then have Writer synthesize the final answer
    - Only finish after both have contributed meaningfully
    """,
        chat_client=chat_client,
    )

    # Build group chat with agent-based orchestrator
    workflow = (
        GroupChatBuilder()
        .with_agent_orchestrator(orchestrator_agent)
        # Set a hard termination condition: stop after 4 assistant messages
        # The agent orchestrator will intelligently decide when to end before this limit but just in case
        .with_termination_condition(lambda messages: sum(1 for msg in messages if msg.role == Role.ASSISTANT) >= 4)
        .participants([researcher, writer])
        .build()
    )

    task = "What are the key benefits of async/await in Python?"

    print(f"Task: {task}\n")
    print("=" * 80)

    final_conversation: list[ChatMessage] = []
    last_executor_id: str | None = None

    # Run the workflow
    async for event in workflow.run_stream(task):
        if isinstance(event, AgentRunUpdateEvent):
            # Print streaming agent updates
            eid = event.executor_id
            if eid != last_executor_id:
                if last_executor_id is not None:
                    print()
                print(f"[{eid}]:", end=" ", flush=True)
                last_executor_id = eid
            print(event.data, end="", flush=True)
        if isinstance(event, WorkflowOutputEvent):
            # Workflow completed - data is a list of ChatMessage
            final_conversation = cast(list[ChatMessage], event.data)

    if final_conversation:
        print("\n\n" + "=" * 80)
        print("Final Conversation:")
        for msg in final_conversation:
            author = getattr(msg, "author_name", "Unknown")
            text = getattr(msg, "text", str(msg))
            print(f"\n[{author}]\n{text}")
            print("-" * 80)

    print("\nWorkflow completed.")

if __name__ == "__main__":
    asyncio.run(main())