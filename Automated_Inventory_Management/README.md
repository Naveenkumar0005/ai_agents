## Agentic AI Inventory Management System

This is an agentic AI inventory mmanagement system. 

It uses the following technologies:
- Python
- OpenAI Agentic SDK
- SQLite database

This program illustrates using AI agents to simulate an 
automated inventory management system.

You need a file named .env with a key OPENAI_API_KEY whose value is
your OpenAI API key:

OPENAI_API_KEY=YOUR_OPENAI_API_KEY

This project uses the uv virtual environment. You may need to execute 
the following commands to install the uv virtual environment tool
and Python packages.

- pip install uv
- uv add "openai>=1.55.0b0" "openai-agents>=0.0.23" --pre

To start this agentic AI system you execute:

uv run main.py

To stop the system press Ctrl + d

You can use this GUI tool to examine the SQLite database:
[SQLite Browser](https://sqlitebrowser.org/)

Note, if you try to execute this agentic AI system and
manipulate the database while the database is open in the
SQLite Browser tool the system calls may fail due to db locks.