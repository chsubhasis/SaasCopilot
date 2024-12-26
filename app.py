import gradio as gr  # type: ignore
from brdgen.brd_workflow import initiate_workflow
import threading
from queue import Queue
from brdgen.brd_utility import Utility


def generate_new_BRD(assessment_file):
    try:
        print("generate_new_BRD")
        assessment_text_gradio = Utility.extract_text(assessment_file.name)
        brd_content, brd_file_path = initiate_workflow(
            assessment_text=assessment_text_gradio
        )
        return brd_content, brd_file_path
    except Exception as e:
        print(e)
        return e, None


"""	
def updated_existing_BRD():
    pass
"""


def create_brd_interface():

    # Create Gradio interface
    with gr.Blocks() as demo:
        gr.Markdown("#Business Requirements Document (BRD) Generator")

        with gr.Row():
            with gr.Column():
                # Assessment Upload
                assessment_input = gr.File(label="Upload Assessment Report")
                generate_btn = gr.Button("Generate BRD")

                # BRD Download
                brd_download = gr.File(label="Download BRD")

                """
                # Feedback Input
                feedback_input = gr.Textbox(
                    label="Refine BRD (Provide Feedback)", lines=5, interactive=True
                )
                refine_btn = gr.Button("Refine BRD")
                """

            with gr.Column():
                # BRD Content Display
                brd_output = gr.Textbox(label="BRD Content", lines=15, interactive=True)

        # Event Handlers
        generate_btn.click(
            generate_new_BRD,
            inputs=assessment_input,
            outputs=[brd_output, brd_download],
            api_name="gererateBRD",
        )

        """
        refine_btn.click(
            updated_existing_BRD,
            inputs=feedback_input,
            outputs=[brd_output, brd_download],
        )
        """

    return demo


if __name__ == "__main__":
    demo = create_brd_interface()
    demo.launch(share=True)
