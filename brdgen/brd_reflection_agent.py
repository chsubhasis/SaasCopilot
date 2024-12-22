class BRDRevisor:
    def refine_brd(self, user_feedback: str) -> str:
            """Refine BRD based on user feedback."""
            if not self.current_brd:
                return "No existing BRD to refine."

            # Prepare context with previous interactions
            messages = [
                {
                    "role": "system", 
                    "content": "Refine the Business Requirements Document based on user feedback."
                },
                {
                    "role": "user", 
                    "content": f"Original Assessment: {self.current_assessment}"
                },
                {
                    "role": "assistant", 
                    "content": f"Here is the current version of the Business Requirements Document (BRD). Please update it based on the feedback. {self.current_brd}"
                },
                {
                    "role": "user", 
                    "content": f"Feedback to incorporate: {user_feedback}"
                }
            ]
            
            # Generate refined BRD
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=self.temperature
            )
            
            # Update context
            self.current_brd = response.choices[0].message.content
            #self.chat_history.append({"user": user_feedback, "assistant": self.current_brd})
            
            return self.current_brd