from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from utils.file_utils import read_file
from dbscripts import database
import pandas as pd

model = LiteLlm(
    model="ollama_chat/llama3.1:8b"
    #model="ollama_chat/qwen3:latest"
)

sql_engine = database.get_engine()


def run_sql_query(query: str) -> list:
    """Returns dataframe of the results after running the SQL query against the PostgreSQL.

    Args:
        query (str): The input query. Run this query against the PostgreSQL DB

    Returns:
        dataframe: dataframe of the results
    """
    print(f'>>>>> The sql engine was called={query} and SQL engine is {sql_engine}')
    df = pd.read_sql(query, con=sql_engine)
    response_list = df.to_dict(orient='records')
    print(f'Response List {response_list}')
    return response_list



instruction_prompt = read_file('prompt/emp_system_prompt.txt')

root_agent = Agent(
    name="DataBase_Agent",
    model=model,
    instruction=instruction_prompt,
    tools=[run_sql_query]
)
