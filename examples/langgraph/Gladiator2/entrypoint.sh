#!/bin/bash
# filepath: /entrypoint.sh

# Start the FastAPI app
uvicorn api:app --host 0.0.0.0 --port 8000 &

# Start the Streamlit app
streamlit run legal_chatbot.py --server.port 8501 --server.address 0.0.0.0

# Wait for background processes
wait