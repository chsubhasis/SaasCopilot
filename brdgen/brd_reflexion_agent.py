from brd_gen_agent import BRDGenerator


class BRDRevisor:
    def __init__(self, brd_generator: BRDGenerator, current_brd: str):
        self.brd_generator = brd_generator  # TODO maybe remove this
        self.client = brd_generator.client
        self.model = brd_generator.model
        self.temperature = brd_generator.temperature
        self.current_assessment = brd_generator.current_assessment
        self.current_brd = current_brd

    def refine_brd(self) -> str:  # TODO self is needed?
        """Refine BRD based on user feedback."""
        if not self.current_brd:
            return "No existing BRD to refine."

        # Prepare context with previous interactions
        messages = [
            {
                "role": "system",
                "content": """
                    You are an experienced Business Requirements Document (BRD) reviewer with extensive experience in SAP implementations.
                    
                    Your task is to:
                    1. Compare the BRD against the original assessment report for accuracy and completeness
                    2. Review the BRD for clarity, conciseness, and professional tone
                    3. Check that each requirement is:
                    - Specific and measurable
                    - Properly categorized (functional vs non-functional)
                    - Aligned with the business needs from the assessment
                    4. Ensure all critical sections are present and properly detailed
                    5. Remove any redundant or irrelevant information
                    6. Verify that technical terminology is used correctly
                    7. Check that dependencies and constraints are clearly stated
                    
                    Provide the revised BRD maintaining the same section structure but with improved content.
                    """,
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
