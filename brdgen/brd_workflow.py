import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

import io
from typing import List, Optional, Dict, Tuple

from brdgen.brd_gen_agent import BRDGenerator
from brdgen.brd_rag_agent import BRDRAG
from brdgen.brd_reflexion_agent import BRDRevisor
from brdgen.brd_state import BRDState
from brdgen.brd_tool_executor import BRDExternalTool
from brdgen.brd_utility import Utility
from dotenv import load_dotenv
from langgraph.graph import END, START, StateGraph
from PIL import Image

load_dotenv()
MODEL = "mistral-large-latest"
MAX_ITERATIONS = 1  # For self critic.. increase if needed


class BRDGraphNode:
    def __init__(self, brd_generator: BRDGenerator):
        self.brd_generator = brd_generator

    def generate_brd(self, state: BRDState) -> BRDState:
        print("Enter into generate_brd")
        try:
            brd_initial_content = self.brd_generator.generate_brd(
                assessment_text=state["assessment_text"],
                rag_results=state["rag_result"],
                save_prompt=False,
            )

            state["brd_content"] = brd_initial_content.selected_brd
            print("brd generated")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_initial_content.selected_brd,
                "iteration_count": 0,
                "rag_result": state["rag_result"],
            }
        except Exception as e:
            print(e)  # TODO log error
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": None,
                "iteration_count": 0,
                "rag_result": state["rag_result"],
            }

    def refine_brd(self, state: BRDState) -> BRDState:
        print("Enter into refine_brd")
        try:
            brd_revisor = BRDRevisor(
                self.brd_generator, state["brd_content"], state["assessment_text"]
            )
            brd_revised_content = brd_revisor.refine_brd()
            state["brd_content"] = brd_revised_content
            print("BRD refined")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_revised_content,
                "iteration_count": state["iteration_count"] + 1,
                "rag_result": state["rag_result"],
            }
        except Exception as e:
            print(e)
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": None,
                "iteration_count": state["iteration_count"],
                "rag_result": state["rag_result"],
            }

    def save_brd(self, state: BRDState) -> BRDState:
        print("Enter into save_brd")
        try:
            brd_content = state["brd_content"]
            if brd_content is None:
                raise ValueError("BRD content is empty")
            brd_path = Utility.save_brd(brd_content)
            print(f"BRD saved at: {brd_path}")
            state["brd_file_path"] = brd_path
            return state
        except Exception as e:
            print(e)
            return state

    def exec_tool_brd(self, state: BRDState) -> BRDState:
        print("Enter into exec_tool_brd")
        try:
            brdtool = BRDExternalTool()  # TODO Sample Tool. Replace with actual tool
            brd_content_tool = brdtool.search()
            updated_brd = state["brd_content"] + brd_content_tool
            print("BRD updated with external tool")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": updated_brd,
                "iteration_count": state["iteration_count"],
                "rag_result": state["rag_result"],
            }
            return state
        except Exception as e:
            print(e)
            return state

    def retrieve_vector(self, state: BRDState) -> BRDState:
        print("Enter into retrieve_vector")
        try:
            brdrag = BRDRAG()
            # assessment_document_paths = [
            #    "new_assessment.pdf"  # TODO - replace with actual path
            # ]
            assessment_document_contents = [
                state["assessment_text"]
                # TODO - update this with other contents provided as input
            ]
            brdrag.load_documents_from_content(assessment_document_contents)
            result = brdrag.retrieveResult("What is the purpose of the assessment?")
            rag_result = result[0].page_content
            state["rag_result"] = rag_result
            print("Retrieved vector from RAG")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": state["brd_content"],
                "iteration_count": state["iteration_count"],
                "rag_result": rag_result,
            }
            return state
        except Exception as e:
            print(e)
            return state


def create_brd_workflow() -> StateGraph:
    # Initialize components
    brd_generator = BRDGenerator(api_key=os.getenv("MISTRAL_API"), model=MODEL)
    node = BRDGraphNode(brd_generator)

    # Create workflow
    workflow = StateGraph(BRDState)

    # Add nodes
    workflow.add_node("retrieve_vector", node.retrieve_vector)
    workflow.add_node("initial_brd_with_self_consistency", node.generate_brd)
    workflow.add_node("execute_tools", node.exec_tool_brd)
    workflow.add_node("self_reflect_brd", node.refine_brd)
    workflow.add_node("save_final_brd", node.save_brd)

    # Set entry point
    workflow.set_entry_point("retrieve_vector")

    # Add edges
    workflow.add_edge("retrieve_vector", "initial_brd_with_self_consistency")
    workflow.add_edge("initial_brd_with_self_consistency", "execute_tools")
    workflow.add_edge("execute_tools", "self_reflect_brd")

    # Define conditional edges for refine_brd
    def route_refinement(state: BRDState) -> str:
        if state["iteration_count"] < MAX_ITERATIONS:
            return "continue_refinement"
        return "refinement_complete"

    workflow.add_conditional_edges(
        "self_reflect_brd",
        route_refinement,
        {
            "continue_refinement": "self_reflect_brd",
            "refinement_complete": "save_final_brd",
        },
    )

    workflow.add_edge("save_final_brd", END)

    return workflow


def initiate_workflow(
    assessment_file,
    user_feedback: Optional[str] = None,  # This will be needed for human in the loop
    brd_content: Optional[str] = None,
):
    print("Initiating BRD workflow")
    workflow = create_brd_workflow()
    app = workflow.compile()

    # Generate workflow diagram
    image_bytes = app.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(image_bytes))
    image.save("brd_workflow.png")

    assessment_text = Utility.extract_text(assessment_file.name)

    initial_state = {
        "assessment_text": assessment_text,
        "brd_content": brd_content,
        "iteration_count": 0,
        "user_feedback": user_feedback,
    }

    result = app.invoke(initial_state)
    print("BRD workflow completed")
    return result["brd_content"], result["brd_file_path"]


"""
# Example usage
if __name__ == "__main__":
    workflow = create_brd_workflow()
    app = workflow.compile()

    # Generate workflow diagram
    image_bytes = app.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(image_bytes))
    image.save("brd_workflow.png")

    assessment_text = Utility.extract_text(
        "new_assessment.pdf"
    )  # Sample assessment file

    initial_state = {
        "assessment_text": assessment_text,
        "brd_content": None,
        "iteration_count": 0,
    }

    result = app.invoke(initial_state)
    print("BRD workflow completed")
"""
