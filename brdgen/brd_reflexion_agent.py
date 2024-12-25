from brdgen.brd_gen_agent import BRDGenerator
import brdgen.brd_prompts as prompts


class BRDRevisor:
    def __init__(
        self, brd_generator: BRDGenerator, current_brd: str, current_assessment: str
    ):
        self.client = brd_generator.client
        self.model = brd_generator.model
        self.temperature = brd_generator.temperature
        self.current_assessment = current_assessment
        self.current_brd = current_brd

    def refine_brd(self) -> str:
        """Refine BRD based on user feedback."""
        print("Refining BRD...")
        if not self.current_brd:
            return "No existing BRD to refine."

        # Prepare context with previous interactions
        messages = [
            {
                "role": "system",
                "content": prompts.REFINE_BRD_PROMPT_SYSTEM,
            },
            {
                "role": "user",
                "content": f"""
                    Please review and improve this BRD based on the original assessment.
                    
                    Original Assessment Report:
                    {self.current_assessment}
                    
                    Current BRD Draft:
                    {self.current_brd}
                    """,
            },
        ]

        # Generate refined BRD
        response = self.client.chat.complete(
            model=self.model, messages=messages, temperature=self.temperature
        )

        # Update context
        self.current_brd = response.choices[0].message.content
        # self.chat_history.append({"user": user_feedback, "assistant": self.current_brd})

        return self.current_brd
