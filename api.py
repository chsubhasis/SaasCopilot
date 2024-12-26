from http.client import HTTPException
import sys
from pathlib import Path
from typing import Any
import tempfile
import os
import pathlib

from brdgen.brd_rag_agent import BRDRAG
from brdgen.brd_utility import Utility
from brdgen.brd_workflow import initiate_workflow
from fastapi import APIRouter, UploadFile, File  # type: ignore
from brdgen.brd_tool_executor import BRDExternalTool

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

api_router = APIRouter()


@api_router.post("/generateBRD", status_code=200)
async def generateBRD(assessment_file: UploadFile = File(...)) -> Any:
    # Get the file extension from the original filename
    original_extension = pathlib.Path(assessment_file.filename).suffix

    with tempfile.NamedTemporaryFile(
        suffix=original_extension, delete=False
    ) as temp_file:
        # Write the uploaded file content to a temporary file
        content = await assessment_file.read()
        temp_file.write(content)
        temp_file.flush()

    assessment_text_fastapi = Utility.extract_text(temp_file.name)
    brd_content, brd_file_path = initiate_workflow(
        assessment_text=assessment_text_fastapi
    )

    # Clean up the temporary file
    # better to keep this in a finally block
    temp_file.close()
    os.unlink(temp_file.name)

    return brd_content


@api_router.get("/searchTool", status_code=200)
def searchTool() -> Any:
    return BRDExternalTool().search()


@api_router.get("/searchRAG", status_code=200)
def searchRAG() -> Any:
    result = BRDRAG().retrieveResult("What is the purpose of the assessment?")
    return result[0].page_content
