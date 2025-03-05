## Company Legal Agent

This is legal support chatbot for company. It can use web search, database with 100 employees, JIRA search and create and retrieveing local documents on supplier liability clauses. It can generate or append existing documents.
The input supplier liability documents that are retrieved for the chatbot are stored in the input_files/supplier_liability_contracts. The newly generated files are stored in the output_files/supplier_liability_contracts and have suffix 'ai_created.docx'.
Employees database contains IDs, names, roles, emails, ages and genders of employees.
For searching the JIRA, it has to be specified which project to search into.

Chatbot uses two LLMs - one that is binded with the tools (gpt3) and the other one that is used for document generation (llama3.1).

## Setup and Installation

### Using Docker

1. **Build the Docker Image**:

   ```sh
   docker build -t legal-agent .
   ```

2. **Run the Docker Container**:

   ```sh
   docker run -p 8000:8000 -p 8501:8501 \
     -v ./input_files:/app/input_files \
     -v ./output_files:/app/output_files \
     legal-agent
   ```

   This command starts both the FastAPI server and the Streamlit app. Access them at:

   - FastAPI: [http://localhost:8000](http://localhost:8000)
   - Streamlit: [http://localhost:8501](http://localhost:8501)

### Without Docker

1. **Install Dependencies**:

   Ensure you have Python 3.11 installed.

   Install the required packages:

   ```sh
   pip install -r requirements.txt
   ```

   **Note**: If the installation fails due to Rust dependencies, install Rust using:

   ```sh
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   ```

   And add Rust to your `PATH`.

2. **Run the FastAPI Server**:

   ```sh
   uvicorn main_agent_clean:app --reload
   ```

3. **Run the Streamlit App**:

   In a new terminal window:

   ```sh
   streamlit run streamlit_app.py
   ```

For starting the chatbot, follow these steps:

1. Create .env file with following keys:
   LANGCHAIN_TRACING_V2,
   LANGCHAIN_API_KEY,
   LANGCHAIN_PROJECT,
   PINECONE_API_KEY,
   AZURE_OPENAI_API_KEY,
   AZURE_OPENAI_ENDPOINT,
   JIRA_API_TOKEN,
   JIRA_USERNAME,
   JIRA_CLOUD,
   JIRA_INSTANCE_URL,
   AWS_ACCESS_KEY_ID,
   AWS_REGION,
   AWS_SECRET_ACCESS_KEY,
   TAVILY_API_KEY,
   JIRA_project_key

2. Create virtual environment, activate it and install all the dependencies from the requirements.txt with the command:
   **pip install -r requirements.txt**

3. Start the application with command:
   **streamlit run legal_chatbot.py**
