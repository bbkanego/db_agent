**Error when Installing Packages using pip**
- If you are on Ubuntu and you have the venv activated and you run 
    the "pip install" command, the issue might be that incorrect pip is being used.
- So you need to make sure that you are using the pip3 that is part of "venv/bin" dir.
- Thus try using the - (bkvenv) bkane@bkvictus:~/code/python/db_agent$ pip3 install chainlit

### References:
1. https://medium.com/google-cloud/building-interactive-agentic-applications-using-adk-and-ag-ui-protocol-3a49ae6d3dc9
2. https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#full-example-code-development-pipeline
3. 

**How to run the ADK Agents**
1. Each ADK agent has their own directories.
2. Example [adk_db_agent_with_tools](adk_db_agent_with_tools), "[adk_sql_agent_no_tools](adk_sql_code_generator_agent)"
3. You need to navigate into "top" level folder i.e. /python/db_agent and the run the "adk web" command like below:
    - (.venv) bkane@bkvictus:~/code/python/db_agent$ adk-web


### Building an AGENT team
- Refer this: https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial
- The collab version of Agent Team is here: https://google.github.io/adk-docs/tutorials/agent-team/#step-1-your-first-agent-basic-weather-lookup
- 