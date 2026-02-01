from typing import Optional

from google.adk.agents import SequentialAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.apps import App
from google.adk.models import LlmRequest, LlmResponse
from google.adk.plugins import ReflectAndRetryToolPlugin

from reusable_agents import sql_code_generator_agent, sql_code_review_agent, sql_code_runner_agent

########################################## SQL Code Runner Agent ##########################################
sql_code_runner_agent_local = sql_code_runner_agent.create_sql_runner_agent()
########################################## SQL Code Runner Agent ##########################################

########################################## SQL Code review Agent ##########################################
sql_code_review_agent_local = sql_code_review_agent.create_code_review_agent()
sql_code_review_agent_local.output_key="sql_review_result"
print(f'>>>> The code review agent is {sql_code_review_agent_local}')
########################################## ^^^ SQL Code review Agent ^^^ ##########################################

########################################## SQL Creation Agent ##########################################
def sql_creation_state(callback_context: CallbackContext, llm_request: LlmRequest
                       ) -> Optional[LlmResponse]:
    print(f'The callback context is {callback_context}, and the LLM request is {llm_request}')
    # return LlmResponse(
    #     content=Content(
    #         role="model",  # Mimic a response from the agent's perspective
    #         parts=[Part(
    #             text=f"Processing your Request now...")],
    #     )
    # )

sql_creation_agent_local = sql_code_generator_agent.code_generator_agent()
sql_creation_agent_local.before_model_callback = sql_creation_state
sql_creation_agent_local.output_key = "generated_sql" # Stores output in state['generated_sql']
########################################## ^^^ SQL Creation Agent ^^^ ##########################################

root_agent = SequentialAgent(
    name="Text_To_SQL_Code_Pipeline_Agent",
    sub_agents=[sql_creation_agent_local, sql_code_review_agent_local, sql_code_runner_agent_local]
)

'''
With this configuration, if any tool called by an agent returns an error, 
the request is updated and tried again, up to a maximum of 3 attempts, per tool.
'''
app = App(
    name="adk_db_multi_agent", ## this should match the folder name
    root_agent=root_agent,
    plugins=[
        ReflectAndRetryToolPlugin(max_retries=5,
                                    ## This ensures that if the retries fail, the error details are formatted into
                                  # a message and sent back to the agent as part of the normal conversation flow,
                                  # allowing the agent to analyze it and decide on an alternative approach
                                  # or inform the user.
                                  throw_exception_if_retry_exceeded=False),
    ],
)
