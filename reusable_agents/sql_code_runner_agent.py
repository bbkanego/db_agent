import json
import logging
import traceback

import pandas as pd
from google.adk.agents import LlmAgent
from google.adk.models import LiteLlm
from google.adk.tools import ToolContext
from google.genai.types import GenerateContentConfig

from dbscripts import database
from model.common_models import SqlReviewOutput

model_sql_runner_agent = LiteLlm(
    # model="ollama_chat/llama3.1:8b"
    model="ollama_chat/qwen3:latest"
)

sql_runner_agent_config = GenerateContentConfig(
    temperature=1.0,
    # max_output_tokens=2048,
    top_p=0.85,
    top_k=30
)


def parse_sql_review(json_data: dict | str) -> SqlReviewOutput:
    try:
        if isinstance(json_data, str):
            return SqlReviewOutput.model_validate_json(json_data)
        else:
            return SqlReviewOutput.model_validate(json_data)
    except Exception as e:  # pydantic.ValidationError or JSON decode error
        raise ValueError(f"Invalid SQL review output format: {e}") from e


sql_engine = database.get_engine()


def run_sql_query(tool_context: ToolContext) -> dict:
    """Returns dataframe of the results after running the SQL query against the PostgreSQL.

    Args:
        tool_context(CallbackContext): This is the tool callback context

    Returns:
        dict: Dictionary of the results
    """
    query = tool_context.state.get("generated_sql")
    print(f'>>> The incoming query in "generated_sql" is {query}')
    if type(query) is dict:
        query = json.dumps(query)

    sql_review_result: str = tool_context.state.get("sql_review_result")
    if sql_review_result:
        review_result: SqlReviewOutput = parse_sql_review(sql_review_result)
        if len(review_result.syntax_issues) > 0:
            raise Exception('In valid SQL...')

    try:
        query = query.replace("```sql", "").replace("```", "")
        print(f'>>>>> The sql code review result is {sql_review_result}')
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
    except Exception as e:
        logging.error(traceback.format_exc())  # Log the full traceback
        print(f"An unexpected error occurred: {e}")
        # after catching raise it, so the model can retry
        raise e


def create_sql_runner_agent():
    return LlmAgent(
        name="SQL_Code_Runner_Agent",
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