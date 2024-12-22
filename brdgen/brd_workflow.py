from langgraph.graph import END, StateGraph, START
from brd_gen_agent import BRDGenerator
from brd_reflection_agent import BRDRevisor
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
            state["brd_content"] = brd_initial_content
            print("brd generated successfully")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_initial_content,
            }
        except Exception as e:
            print(e)
            # TODO: Log error
            return {"assessment_text": state["assessment_text"], "brd_content": None}

    def refine_brd(self, state: BRDState) -> BRDState:
        try:
            brd_revisor = BRDRevisor(self.brd_generator, state["brd_content"])
            brd_revised_content = brd_revisor.refine_brd()
            state["brd_content"] = brd_revised_content
            print("brd refined successfully")
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_revised_content,
            }
        except Exception as e:
            print(e)
            # TODO: Log error
            return {"assessment_text": state["assessment_text"], "brd_content": None}

    def save_brd(self, state: BRDState) -> BRDState:
        try:
            brd_content = state["brd_content"]
            if brd_content is None:
                raise ValueError("BRD content is empty")

            # Save BRD
            brd_path = Utility.save_brd(brd_content)
            print(f"BRD saved at: {brd_path}")
            return state
        except Exception as e:
            print(e)


def create_brd_workflow() -> StateGraph:
    # Initialize components
    brd_generator = BRDGenerator(api_key=os.getenv("MISTRAL_API"), model=MODEL)
    node = BRDGraphNode(brd_generator)

    # Create workflow
    workflow = StateGraph(BRDState)
    workflow.add_node("generate_brd", node.generate_brd)
    workflow.set_entry_point("generate_brd")
    workflow.add_node("refine_brd", node.refine_brd)
    workflow.add_node("save_brd", node.save_brd)

    # Add edge to end when complete
    workflow.add_edge("generate_brd", "refine_brd")

    workflow.add_edge("refine_brd", "save_brd")
    workflow.add_edge("save_brd", END)

    return workflow


# Example usage
if __name__ == "__main__":
    workflow = create_brd_workflow()
    app = workflow.compile()

    image_bytes = app.get_graph().draw_mermaid_png()
    image = Image.open(io.BytesIO(image_bytes))
    image.save("brd_workflow.png")

    initial_state = {
        "assessment_text": "SAP sample assessment text... will be replaced with DDA file",
        "brd_content": None,
    }

    result = app.invoke(initial_state)
    print("BRD workflow completed")
