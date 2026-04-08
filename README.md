## Architecture

This agent uses a local LLM (via LM Studio) to decide 
when to call Google Calendar tools based on user input.

![Flow diagram](docs/flow.png)

To run

In src:

- uvicorn api.main:app --reload

In browser:
- http://localhost:8000/auth/login