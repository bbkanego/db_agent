from google.adk.agents import LlmAgent
from google.adk.models import LiteLlm
from google.genai.types import GenerateContentConfig

from model.common_models import SqlReviewInput, SqlReviewOutput
from utils.file_utils import read_file

code_review_instructions = read_file('prompt/emp_code_review_v1.txt')

model_code_review_agent = LiteLlm(
    #model="ollama_chat/llama3.1:8b"
    model="ollama_chat/qwen3:latest"
)

sql_code_review_config = GenerateContentConfig(
    temperature=0,
    # max_output_tokens=2048,
    top_p=0.85,
    top_k=30
)

def create_code_review_agent():
    return LlmAgent(
        name="SQL_Code_Review_Agent",
        model=model_code_review_agent,
        instruction=code_review_instructions,
        generate_content_config=sql_code_review_config,
        input_schema=SqlReviewInput,
        output_schema=SqlReviewOutput
    )