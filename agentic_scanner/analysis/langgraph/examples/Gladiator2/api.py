from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel
import uuid

from prompts.prompts import sys_msg
from graph import create_workflow

app = FastAPI()

class QueryRequest(BaseModel):
    message: str
    session_id: Optional[str] = None

@app.post("/query")
async def query(request: QueryRequest):
    graph = create_workflow()

    if request.session_id is None:
        thread_id = str(uuid.uuid4())
    else:
        thread_id = request.session_id

    # Process the message using the langchain workflow
    response = graph.invoke({
                            "messages": [
                                    "user",
                                    request.message
                            ],
                        },
                        # Maximum number of steps to take in the graph - check hot connect this to 5
                        config = {
                            "recursion_limit": 50,
                            "configurable": {
                                # Checkpoints are accessed by thread_id
                                "thread_id": thread_id,
                            }
                        })
    
    return {"response": response['result']}