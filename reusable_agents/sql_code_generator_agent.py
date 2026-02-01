from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.genai.types import GenerateContentConfig

from utils.file_utils import read_file

model = LiteLlm(
    #model="ollama_chat/llama3.1:8b"
    #model="ollama_chat/codegemma:latest"
    model="ollama_chat/qwen3-coder:30b"
    # model="ollama_chat/pxlksr/defog_sqlcoder-7b-2:F16"
    #model="ollama_chat/qwen3:latest"
)

instruction_prompt = read_file('prompt/emp_system_prompt_sql_code_generate_v1.txt')

generate_config = GenerateContentConfig(
    temperature=0,
    #max_output_tokens=2048,
    top_p=0.85,
    top_k=30
)

''' this is recommended, but Ollama_chat does not support the presence_penalty...
generate_config = GenerateContentConfig(
    temperature=0.2,
    #max_output_tokens=2048,
    top_p=0.9,
    top_k=40,
    frequency_penalty=0.8,     # ← start here
    presence_penalty=0.4      # ← adjust together
)
'''

def code_generator_agent():
    return LlmAgent(
        name="SQL_Creation_Agent",
        model=model,
        instruction=instruction_prompt,
        generate_content_config=generate_config
    )
