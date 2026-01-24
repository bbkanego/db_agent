from platform import system


import chainlit as cl
import pandas as pd
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from utils import file_utils
from dbscripts import database

#ollama_llm = ChatOllama(model="llama3.1:8b", temperature=0.7)
ollama_llm = ChatOllama(model="gemma3:12b", temperature=0.7)

load_dotenv()

sql_engine = database.get_engine()

def run_sql_query(query: str) -> dict:
    """Returns dataframe of the results after running the SQL query against the PostgreSQL.

    Args:
        query (str): The input query. Run this query against the PostgreSQL DB

    Returns:
        dataframe: dataframe of the results
    """
    print(f'>>>>> The sql engine was called={query} and SQL engine is {sql_engine}')
    df = pd.read_sql(query, con=sql_engine)
    response_list = df.to_dict(orient='records')
    list_len = len(response_list)
    response = {
        "result": response_list,
        "total_records": list_len,
    }
    if list_len > 20:
        response_list = response_list[:20]
        response = {
            "result": response_list,
            "total_records": list_len,
            "extra_info": f"The results exceed 20 and thus were truncated. The total records are {list_len}"
        }
    print(f'Returning below response \n\n {response} \n\n')
    return response

@cl.on_chat_start
async def on_chat_start():
    print("Chat started")
    await cl.Message(content='Welcome to the Agent. How can I help you today?').send()


@cl.on_chat_end
async def on_chat_end():
    print('Chat ended')


@cl.on_message
async def process_message(user_input: cl.Message):
    file_content = file_utils.read_file('prompt/emp_system_prompt_v1.txt')
    print(f'The file content is = {file_content}')

    input_message = [
        ("system", file_content),
        ("human", user_input.content)
    ]

    response = ollama_llm.invoke(input_message)
    results = run_sql_query(response.content)

    await cl.Message(content=results).send()
