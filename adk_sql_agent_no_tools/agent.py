from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.genai.types import GenerateContentConfig

from utils.file_utils import read_file

model = LiteLlm(
    #model="ollama_chat/llama3.1:8b"
    #model="ollama_chat/qwen3-coder:30b"
    # model="ollama_chat/pxlksr/defog_sqlcoder-7b-2:F16"
    model="ollama_chat/qwen3:latest"
)

instruction_prompt = read_file('prompt/emp_system_prompt_no_tools_v1.txt')

generate_config = GenerateContentConfig(
    temperature=0,
    #max_output_tokens=2048,
    top_p=1.0
)

root_agent = Agent(
    name="DataBase_No_tools_Agent",
    model=model,
    instruction=instruction_prompt,
    generate_content_config=generate_config
)
