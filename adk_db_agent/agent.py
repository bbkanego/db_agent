from typing import Dict

from google.adk.agents import Agent
from google.adk.agents.callback_context import CallbackContext
from google.adk.tools.tool_context import ToolContext
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.genai.types import Part, Blob

from utils.file_utils import read_file
from dbscripts import database
import pandas as pd
from fpdf import FPDF # Requires: pip install fpdf2

model = LiteLlm(
    model="ollama_chat/llama3.1:8b"
    # model="ollama_chat/qwen3:latest"
)

sql_engine = database.get_engine()


def run_sql_query(query: str, tool_context: ToolContext) -> dict:
    """Returns dataframe of the results after running the SQL query against the PostgreSQL.

    Args:
        query (str): The input query. Run this query against the PostgreSQL DB
        tool_context(CallbackContext): This is the tool callback context

    Returns:
        dataframe: dataframe of the results
    """
    print(f'>>>>> The sql engine was called={query} and SQL engine is {sql_engine}')
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


def generate_valid_pdf_bytes(text_content: str) -> bytes:
    """
    Generates a complete, valid PDF file in memory and returns its binary content.
    """
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, text_content)
    # The 'S' destination returns the document as a raw byte string.
    return pdf.output(dest='S')

"""
Saves the provided content as a downloadable Artifact using the ADK framework.
"""
async def create_download_file(file_name:str = 'download_test',
                               mime_type: str = 'text/plain',
                               tool_context: ToolContext = None,
                               ) -> Dict[str, any]:
    """Returns dataframe of the results after running the SQL query against the PostgreSQL.
    Args:
        file_name(str): This is the name of the file. You can generate a random name for this argument
        mime_type(str): This is mime type. The default value is 'text/plain'
        tool_context(CallbackContext): This is the tool callback context
    Returns:
        Dict: Returns a dictionary
    """
    print(f'>>>>> create_download_file was called with tool context {tool_context}')
    if tool_context is None:
        return {
            "status": "error",
            "message": "Tool context is missing, cannot save artifact.",
        }
    
    file_content = tool_context.state.get('full_result', None)
    if file_content is None:
        return {
            "status": "No_Operation_Performed",
            "message": "Since the ToolContext full_result was None, no download file was created"
        }
    
    print(f'>>>>>> The tool context is = {tool_context}')

    # --- STEP 1: Convert Content to Bytes Based on MIME Type ---
    if mime_type == "application/pdf":
        content_bytes = generate_valid_pdf_bytes(file_content)
    else:
        # Use simple string encoding for text/csv, text/plain, etc.
        content_bytes = file_content.encode('utf-8')

    # --- STEP 2: Create the ADK Artifact (types.Part) ---
    artifact_part = Part(
        inline_data=Blob(data=content_bytes, mime_type=mime_type)
    )

    # --- STEP 3: Save the Artifact to the ADK System ---
    # save_artifact handles the versioning and makes the file available for download.
    version = await tool_context.save_artifact(
        filename=file_name,
        artifact=artifact_part
    )

    # clear out the data once the download file has been created...
    tool_context.state["full_result"] = None

    # --- STEP 4: Return the structured response ---
    return {
        "status": "success",
        "message": f"File '{file_name}' (version {version}) has been created and is now available for download.",
        # The ADK UI will automatically intercept this response and provide a download link.
    }

# # The FunctionTool automatically parses the docstring
# download_tool = FunctionTool(
#     func=create_download_file
# )

instruction_prompt = read_file('prompt/emp_system_prompt_v1.txt')

root_agent = Agent(
    name="DataBase_Agent",
    model=model,
    instruction=instruction_prompt,
    # When you assign a function to an agent’s tools list, the framework automatically wraps it as a FunctionTool.
    tools=[run_sql_query, create_download_file]
)
