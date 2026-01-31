import asyncio

import pandas as pd
from google.adk.agents import Agent, LlmAgent, SequentialAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.sessions import InMemorySessionService, Session
from google.adk.tools import ToolContext
from google.genai.types import GenerateContentConfig

from dbscripts import database
from utils.file_utils import read_file

# # --- Session Management ---
# # Key Concept: SessionService stores conversation history & state.
# # InMemorySessionService is simple, non-persistent storage for this tutorial.
# session_service = InMemorySessionService()
#
# # Define constants for identifying the interaction context
# APP_NAME = "SQL Agent"
# USER_ID = "bkane"
# SESSION_ID = "session_001"  # Using a fixed ID for simplicity
#
# # Create the specific session where the conversation will happen
# async def init_session(app_name:str,user_id:str,session_id:str) -> Session:
#     local_session = await session_service.create_session(
#         app_name=app_name,
#         user_id=user_id,
#         session_id=session_id
#     )
#     print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
#     return local_session
#
# session = asyncio.run(init_session(APP_NAME,USER_ID,SESSION_ID))


#print(f"Session created: App='{APP_NAME}', User='{USER_ID}', Session='{SESSION_ID}'")

model_sql_runner_agent = LiteLlm(
    model="ollama_chat/llama3.1:8b"
)

sql_runner_agent_config = GenerateContentConfig(
    temperature=1.0,
    # max_output_tokens=2048,
    top_p=0.85,
    top_k=30
)

sql_engine = database.get_engine()

def run_sql_query(tool_context: ToolContext) -> dict:
    """Returns dataframe of the results after running the SQL query against the PostgreSQL.

    Args:
        tool_context(CallbackContext): This is the tool callback context

    Returns:
        dict: Dictionary of the results
    """
    query:str = tool_context.state.get("generated_sql")
    query = query.replace("```sql", "").replace("```", "")
    print(f'>>>>> The sql engine was called using query={query} and SQL engine is {sql_engine}')
    df = pd.read_sql(query, con=sql_engine)
    response_list = df.to_dict(orient='records')
    list_len = len(response_list)
    response = {
        "status": "success",
        "result": response_list,
        "total_records": list_len,
    }
    max_len = 10
    if list_len > max_len:
        truncated_response_list = response_list[:max_len]
        response = {
            "status": "success",
            "result": truncated_response_list,
            "total_records": list_len,
            "extra_info": f"The results exceed {max_len} and thus were truncated. The total records are {list_len}"
        }
        tool_context.state["full_result"] = response_list
    print(f'Returning below response \n\n {response} \n\n')
    return response


sql_runner_agent = LlmAgent(
    name="SQL_Runner_Agent",
    model=model_sql_runner_agent,
    instruction='''
        You are SQL runner agent. As soon as you are called or invoked. You will run the tool called 
        "run_sql_query". This tool will query a PostgresSQL DB and return a JSON response.
        
        The tool "run_sql_query" will return a Dictionary response like the EXAMPLEs below:
        
        {
            "status": "success",
            "result": [
                        {"first_name": "Sam", "last_name": "Yu", "gender": "M", "date_of_hire": "10/11/2020"},
                        {"first_name": "James", "last_name": "Yummr", "gender": "M", "date_of_hire": "10/11/2013"},
                        ..............
                        ..............
                        {"first_name": "Saas", "last_name": "Tech", "gender": "M", "date_of_hire": "10/11/2015"},
                    ]
            "total_records": list_len,
            "extra_info": f"The results exceed 10 and thus were truncated. The total records are 300000"
        }
        
        OR 
        
        {
            "status": "success",
            "result": [
                    {"count": 100}
                ]
            "total_records": 100,
        }
        
        You will take the output of the response of the tool and convert that to Markdown based on below:
        1. If the "result" element in response is JSON of list of records, you will convert that into markdown table.
        2. If the "result" element in response is a single record, you will provide the response by converting into a sentence.
    ''',
    generate_content_config=sql_runner_agent_config,
    tools=[run_sql_query]
)

model_sql_creation_agent = LiteLlm(
    model="ollama_chat/codegemma:latest"
)

prompt_sql_creation_agent = read_file('prompt/emp_system_prompt_no_tools_v1.txt')

config_sql_creation_agent = GenerateContentConfig(
    temperature=0, # we want the model to deterministic as much as possible. No creativity when writing code.
    # max_output_tokens=2048,
    top_p=0.85,
    top_k=30
)

code_review_instructions = (f"You are SQL Code Review agent. "
                            f"Your job is to review the code based on below instructions:"
                            f"1. Review the instructions first and understand them {prompt_sql_creation_agent}"
                            f"2. Next code review the input query 'generated_sql' for correctness of SQL based on step 1"
                            f"")

sql_code_review_agent = LlmAgent(
    name="SQL_Code_Review_Agent",
    model=model_sql_runner_agent,
    instruction=code_review_instructions,
    generate_content_config=sql_runner_agent_config
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

sql_creation_agent = LlmAgent(
    name="SQL_Creation_Agent",
    model=model_sql_creation_agent,
    instruction=prompt_sql_creation_agent,
    generate_content_config=config_sql_creation_agent,
    output_key="generated_sql" # Stores output in state['generated_sql']
)

root_agent = SequentialAgent(
    name="Text_To_SQL_Code_Pipeline_Agent",
    sub_agents=[sql_creation_agent, sql_runner_agent]
)


