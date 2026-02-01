**Error when Installing Packages using pip**
- If you are on Ubuntu and you have the venv activated and you run 
    the "pip install" command, the issue might be that incorrect pip is being used.
- So you need to make sure that you are using the pip3 that is part of "venv/bin" dir.
- Thus try using the - (bkvenv) bkane@bkvictus:~/code/python/db_agent$ pip3 install chainlit

### References:
1. https://medium.com/google-cloud/building-interactive-agentic-applications-using-adk-and-ag-ui-protocol-3a49ae6d3dc9
2. https://google.github.io/adk-docs/agents/workflow-agents/sequential-agents/#full-example-code-development-pipeline
3. 

### How to run the ADK Agents
#### Option 1: For local testing use "adk web" command
1. Each ADK agent has their own directories.
2. Example [adk_db_agent_with_tools](adk_db_agent_with_tools), "[adk_sql_agent_no_tools](adk_sql_code_generator_agent)"
3. You need to navigate into "top" level folder i.e. /python/db_agent and the run the "adk web" command like below:
    - (.venv) bkane@bkvictus:~/code/python/db_agent$ adk-web

#### Option 2: In PROD the agent is run as a service using "adk api_server".
Reference: https://google.github.io/adk-docs/deploy/cloud-run/#testing-your-agent
1. Once the API Server starts running you need to follow the below steps:
2. Check what apps are there:
    ```bash
      curl 'http://127.0.0.1:8000/list-apps'
    ```
3. Next create a session:
    ```bash
      curl POST 'http://127.0.0.1:8000/apps/adk_db_multi_agent/users/bkane/sessions/session_abc' \
          --header 'Content-Type: application/json' \
          --body '{
            "preferred_language": "English",
            "visit_count": 5
        }'
    ```
4. Finally call the agent you want:
    ```bash
      curl POST 'http://127.0.0.1:8000/run_sse' \
          --header 'Content-Type: application/json' \
          --body '{
            "app_name": "adk_db_multi_agent",
            "user_id": "bkane",
            "session_id": "session_abc",
            "new_message": {
                "role": "user",
                "parts": [
                    {
                        "text": "If the top 20 earning employees from each department leave, how much can the company save over the next 5 years?"
                    }
                ]
            },
            "streaming": false
        }'
    ```

### Building an AGENT team
- Refer this: https://github.com/google/adk-docs/tree/main/examples/python/tutorial/agent_team/adk-tutorial
- The collab version of Agent Team is here: https://google.github.io/adk-docs/tutorials/agent-team/#step-1-your-first-agent-basic-weather-lookup
- 