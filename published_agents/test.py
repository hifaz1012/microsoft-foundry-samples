# filepath: Direct OpenAI compatible approach
from openai import OpenAI 
from azure.identity import DefaultAzureCredential, get_bearer_token_provider 

# edit base_url with your <foundry-resource-name>, <project-name>, and <app-name>
openai = OpenAI(
    api_key=get_bearer_token_provider(DefaultAzureCredential(), "https://ai.azure.com/.default"),
    base_url="https://agents-build2026-resource.services.ai.azure.com/api/projects/agents-build2026/applications/MyAgent/protocols/openai",
    default_query = {"api-version": "2025-11-15-preview"}
)

response = openai.responses.create( 
  input="Write a haiku", 
) 
print(f"Response output: {response.output_text}")