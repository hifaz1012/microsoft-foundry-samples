import asyncio
from typing import Any
from agent_framework import ChatMessage, Role
from agent_framework.azure import AzureOpenAIChatClient
from azure.identity import DefaultAzureCredential
from agent_framework import ConcurrentBuilder

async def main() -> None:
    # 1) Create three domain agents using AzureChatClient
    chat_client = AzureOpenAIChatClient(credential=DefaultAzureCredential())

    researcher = chat_client.create_agent(
        instructions=(
            "You're an expert market and product researcher. Given a prompt, provide concise, factual insights,"
            " opportunities, and risks."
        ),
        name="researcher",
    )

    marketer = chat_client.create_agent(
        instructions=(
            "You're a creative marketing strategist. Craft compelling value propositions and target messaging"
            " aligned to the prompt."
        ),
        name="marketer",
    )

    legal = chat_client.create_agent(
        instructions=(
            "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, and policy concerns"
            " based on the prompt."
        ),
        name="legal",
    )

    # 2) Build a concurrent workflow
    # Participants are either Agents (type of AgentProtocol) or Executors
    workflow = ConcurrentBuilder().participants([researcher, marketer, legal]).build()

    from agent_framework import ChatMessage, WorkflowOutputEvent

    # 3) Run with a single prompt, stream progress, and pretty-print the final combined messages
    output_evt: WorkflowOutputEvent  | None = None
    async for event in workflow.run_stream("We are launching a new budget-friendly electric bike for urban commuters."):
        if isinstance(event, WorkflowOutputEvent):
            output_evt = event

    if output_evt:
        print("===== Final Aggregated Conversation (messages) =====")
        messages: list[ChatMessage] | Any = output_evt.data
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name if msg.author_name else "user"
            print(f"{'-' * 60}\n\n{i:02d} [{name}]:\n{msg.text}")

    # Define a custom aggregator callback that uses the chat client to summarize
    # async def summarize_results(results: list[Any]) -> str:
    #     # Extract one final assistant message per agent
    #     expert_sections: list[str] = []
    #     for r in results:
    #         try:
    #             messages = getattr(r.agent_run_response, "messages", [])
    #             final_text = messages[-1].text if messages and hasattr(messages[-1], "text") else "(no content)"
    #             expert_sections.append(f"{getattr(r, 'executor_id', 'expert')}:\n{final_text}")
    #         except Exception as e:
    #             expert_sections.append(f"{getattr(r, 'executor_id', 'expert')}: (error: {type(e).__name__}: {e})")

    #     # Ask the model to synthesize a concise summary of the experts' outputs
    #     system_msg = ChatMessage(
    #         Role.SYSTEM,
    #         text=(
    #             "You are a helpful assistant that consolidates multiple domain expert outputs "
    #             "into one cohesive, concise summary with clear takeaways. Keep it under 200 words."
    #         ),
    #     )
    #     user_msg = ChatMessage(Role.USER, text="\n\n".join(expert_sections))

    #     response = await chat_client.get_response([system_msg, user_msg])
    #     # Return the model's final assistant text as the completion result
    #     return response.messages[-1].text if response.messages else ""
    
    # # 4) Run again with custom aggregation and print the summary
    # workflow = (
    # ConcurrentBuilder()
    # .participants([researcher, marketer, legal])
    # .with_aggregator(summarize_results)
    # .build()
    # )

    # output_evt: WorkflowOutputEvent | None = None
    # async for event in workflow.run_stream("We are launching a new budget-friendly electric bike for urban commuters."):
    #     if isinstance(event, WorkflowOutputEvent):
    #         output_evt = event

    # if output_evt:
    #     print("===== Final Consolidated Output =====")
    #     print(output_evt.data)

if __name__ == "__main__":
    asyncio.run(main())