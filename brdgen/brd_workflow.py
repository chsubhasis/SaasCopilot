from langgraph.graph import END, StateGraph, START
from brd_gen_agent import BRDGenerator
from brd_reflection_agent import BRDRevisor
from brd_tool_executor import BRDExternalTool
from dotenv import load_dotenv
from brd_state import BRDState
from brd_utility import Utility
from PIL import Image
import io
import os

load_dotenv()
MODEL = "mistral-large-latest"
MAX_ITERATIONS = 2  # For self critic


class BRDGraphNode:
    def __init__(self, brd_generator: BRDGenerator):
        self.brd_generator = brd_generator

    def generate_brd(self, state: BRDState) -> BRDState:
        try:
            brd_initial_content = self.brd_generator.generate_brd(
                state["assessment_text"]
            )
            print("BRD generated")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_initial_content,
                "iteration_count": 0,
            }
        except Exception as e:
            print(e)  # TODO log error
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": None,
                "iteration_count": 0,
            }

    def refine_brd(self, state: BRDState) -> BRDState:
        try:
            brd_revisor = BRDRevisor(self.brd_generator, state["brd_content"])
            brd_revised_content = brd_revisor.refine_brd()
            print("BRD refined")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_revised_content,
                "iteration_count": state["iteration_count"] + 1,
            }
        except Exception as e:
            print(e)
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": None,
                "iteration_count": state["iteration_count"],
            }

    def save_brd(self, state: BRDState) -> BRDState:
        try:
            brd_content = state["brd_content"]
            if brd_content is None:
                raise ValueError("BRD content is empty")
            brd_path = Utility.save_brd(brd_content)
            print(f"BRD saved at: {brd_path}")
            return state
        except Exception as e:
            print(e)
            return state

    def exec_tool_brd(self, state: BRDState) -> BRDState:
        try:
            brdtool = BRDExternalTool()  # TODO Sample Tool. Replace with actual tool
            brd_content_tool = brdtool.search()
            updated_brd = state["brd_content"] + brd_content_tool
            print("BRD updated with external tool")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": updated_brd,
                "iteration_count": state["iteration_count"],
            }
            return state
        except Exception as e:
            print(e)
            return state

    def retrieve_vector(self, state: BRDState) -> BRDState:
        print("Retrieved vector")
        pass


def create_brd_workflow() -> StateGraph:
    # Initialize components
    brd_generator = BRDGenerator(api_key=os.getenv("MISTRAL_API"), model=MODEL)
    node = BRDGraphNode(brd_generator)

    # Create workflow
    workflow = StateGraph(BRDState)

    # Add nodes
    workflow.add_node("generate_brd", node.generate_brd)
    workflow.add_node("exec_tool", node.exec_tool_brd)
    workflow.add_node("retrieve_vector", node.retrieve_vector)
    workflow.add_node("self_refine_brd", node.refine_brd)
    workflow.add_node("save_brd", node.save_brd)

    # Set entry point
    workflow.set_entry_point("generate_brd")

    workflow.add_edge("generate_brd", "exec_tool")
    workflow.add_edge("exec_tool", "retrieve_vector")
    workflow.add_edge("retrieve_vector", "self_refine_brd")

    # Define conditional edges for refine_brd
    def route_refinement(state: BRDState) -> str:
        if state["iteration_count"] < MAX_ITERATIONS:
            return "continue_refinement"
        return "refinement_complete"

    workflow.add_conditional_edges(
        "self_refine_brd",
        route_refinement,
        {"continue_refinement": "self_refine_brd", "refinement_complete": "save_brd"},
    )

    # Add edge from save_brd to END
    workflow.add_edge("save_brd", END)

    return workflow


# Example usage
if __name__ == "__main__":
    workflow = create_brd_workflow()
    app = workflow.compile()

    # Generate workflow diagram
    image_bytes = app.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(image_bytes))
    image.save("brd_workflow.png")

    initial_state = {
        "assessment_text": "SAP sample assessment text... will be replaced with DDA file",
        "brd_content": None,
        "iteration_count": 0,
    }

    result = app.invoke(initial_state)
    print("BRD workflow completed")
