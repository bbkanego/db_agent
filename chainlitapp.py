from platform import system


import chainlit as cl
from dotenv import load_dotenv
from langchain_ollama import ChatOllama

from dbscripts.database import get_db_connection
from utils import file_utils

#ollama_llm = ChatOllama(model="llama3.1:8b", temperature=0.7)
ollama_llm = ChatOllama(model="gemma3:12b", temperature=0.7)

load_dotenv()

@cl.on_chat_start
async def on_chat_start():
    print("Chat started")
    await cl.Message(content='Welcome to the Agent. How can I help you today?').send()


@cl.on_chat_end
async def on_chat_end():
    print('Chat ended')


@cl.on_message
async def process_message(user_input: cl.Message):
    file_content = file_utils.read_file('prompt/emp_system_prompt.txt')
    print(f'The file content is = {file_content}')

    input_message = [
        ("system", file_content),
        ("human", user_input.content)
    ]

    response = ollama_llm.invoke(input_message)
    connection = run_sql()
    print(f'The connection is {connection}')

    await cl.Message(content=response.content).send()
