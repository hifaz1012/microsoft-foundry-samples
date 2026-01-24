# Copyright (c) Microsoft. All rights reserved.
import asyncio
import os
from random import randint
from typing import Annotated

from agent_framework.azure import AzureAIClient
from azure.ai.projects.aio import AIProjectClient
from azure.identity.aio import AzureCliCredential
from pydantic import Field
from dotenv import load_dotenv

"""
Azure AI Agent Existing Conversation Example

This sample demonstrates usage of AzureAIClient with existing conversation created on service side.
"""
load_dotenv(".env")

def get_weather(
    location: Annotated[str, Field(description="The location to get the weather for.")],
) -> str:
    """Get the weather for a given location."""
    conditions = ["sunny", "cloudy", "rainy", "stormy"]
    return f"The weather in {location} is {conditions[randint(0, 3)]} with a high of {randint(10, 30)}°C."

async def example_with_thread() -> None:
    """This example shows how to specify existing conversation ID with AgentThread."""
    print("=== Azure AI Agent With Existing Conversation and Thread ===")
    async with (
        AzureCliCredential() as credential,
        AIProjectClient(endpoint=os.environ["AZURE_AI_PROJECT_ENDPOINT"], credential=credential) as project_client,
        AzureAIClient(project_client=project_client).as_agent(
            name="BasicAgent",
            instructions="You are a helpful agent.",
            tools=get_weather,
        ) as agent,
    ):
        # Create a conversation using OpenAI client
        openai_client = project_client.get_openai_client()
        conversation = await openai_client.conversations.create()
        conversation_id = conversation.id
        print(f"Conversation ID: {conversation_id}")

        # Create a thread with the existing ID
        thread = agent.get_new_thread(service_thread_id=conversation_id)

        query = "What's the weather like in Seattle?"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")

        query = "What was my last question?"
        print(f"User: {query}")
        result = await agent.run(query, thread=thread)
        print(f"Agent: {result.text}\n")


async def main() -> None:
    await example_with_thread()


if __name__ == "__main__":
    asyncio.run(main())