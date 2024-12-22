from langgraph.graph import END, StateGraph, START
from brd_gen_agent import BRDGenerator
from dotenv import load_dotenv
from brd_state import BRDState
from PIL import Image
import io
import os
load_dotenv()

MODEL = 'mistral-large-latest'

class BRDGraphNode:
    def __init__(self, brd_generator: BRDGenerator):
        self.brd_generator = brd_generator
    
    def generate_brd(self, state: BRDState) -> BRDState:
        try:
            brd_content = self.brd_generator.generate_brd(state["assessment_text"])
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": brd_content
            }
        except Exception as e:
            print(f"Error: {str(e)}")
            #TODO: Log error
            return {
                "assessment_text": state["assessment_text"],
                "brd_content": None
            }

def create_brd_workflow() -> StateGraph:
    # Initialize components
    brd_generator = BRDGenerator(api_key=os.getenv('MISTRAL_API'), model=MODEL)
    node = BRDGraphNode(brd_generator)
    
    # Create workflow
    workflow = StateGraph(BRDState)
    workflow.add_node("generate_brd", node.generate_brd)
    workflow.set_entry_point("generate_brd")
    
    # Add edge to end when complete
    workflow.add_edge("generate_brd", END)
    
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
        "brd_content": None
    }
    
    result = app.invoke(initial_state)
    #print(result)
    print("brd generated successfully")