from http.client import HTTPException
import sys
from pathlib import Path
from typing import Any
import tempfile
import os
import pathlib
import uuid

#from brdgen.brd_rag_agent import BRDRAG
from brdgen.brd_utility import Utility
from brdgen.brd_workflow import initiate_workflow
from fastapi import APIRouter, UploadFile, File, BackgroundTasks  # type: ignore
from brdgen.brd_tool_executor import BRDExternalTool

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

api_router = APIRouter()

# This dictionary stores the status and result of tasks
task_status = {}

# Helper function to initiate the workflow (long-running task)
def initiate_workflow_background(assessment_text: str, temp_file_path: str, task_id: str):
    try:
        # Long-running task
        brd_content, brd_file_path = initiate_workflow(assessment_text)

        # Once the task is done, update the task status
        task_status[task_id] = {"status": "completed", "brd_content": brd_content}
        
    except Exception as e:
        task_status[task_id] = {"status": "failed", "error": str(e)}
    finally:
        os.remove(temp_file_path)  # Clean up the temporary file when done

@api_router.post("/generateBRD", status_code=200)
async def generate_BRD(background_tasks: BackgroundTasks, assessment_file: UploadFile = File(...)) -> Any:
    # Generate a unique task ID
    task_id = str(uuid.uuid4())

    # Get the file extension from the original filename
    original_extension = pathlib.Path(assessment_file.filename).suffix

    with tempfile.NamedTemporaryFile(
        suffix=original_extension, delete=False
    ) as temp_file:
        # Write the uploaded file content to a temporary file
        content = await assessment_file.read()
        temp_file.write(content)
        temp_file.flush()

    # Extract text from the uploaded assessment file
    assessment_text_fastapi = Utility.extract_text(temp_file.name)

    # Add the long-running task to the background tasks
    background_tasks.add_task(initiate_workflow_background, assessment_text_fastapi, temp_file.name, task_id)

    task_status[task_id] = {"status": "BRD generation In-progress"}

    # Return the task ID to the client
    return {"message": "BRD generation started, please check back later.", "task_id": task_id}

@api_router.get("/checkTaskStatus/{task_id}", status_code=200)
async def check_task_status(task_id: str) -> Any:
    # Check the status of the task based on the task_id
    task = task_status.get(task_id)

    if not task:
        return {"message": "Task ID not found."}

    # Return task status and result if completed
    return task

@api_router.get("/searchTool", status_code=200)
def search_Tool() -> Any:
    return BRDExternalTool().search()


"""
@api_router.get("/searchRAG", status_code=200)
def search_RAG() -> Any:
    result = BRDRAG().retrieveResult("What is the purpose of the assessment?")
    return result[0].page_content
""" 