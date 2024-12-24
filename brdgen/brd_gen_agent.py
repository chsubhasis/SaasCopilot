from typing import List, Optional, Dict
from mistralai import Mistral
from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from brd_utility import Utility
from datetime import datetime
import os
from difflib import SequenceMatcher
import statistics
from concurrent.futures import ThreadPoolExecutor
from dotenv import load_dotenv
import brd_prompts as prompts

load_dotenv()


class BRDGenerator:

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.3,
        num_samples: int = 2,  # TODO - Finalize the number of samples for self consistency
        similarity_threshold: float = 0.8,
    ):
        self.client = Mistral(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.few_shot_examples = []
        self.num_samples = num_samples
        self.similarity_threshold = similarity_threshold
        self.prompts_dir = "prompts"
        os.makedirs(self.prompts_dir, exist_ok=True)

    def load_examples(self, assessment_paths: List[str], brd_paths: List[str]) -> None:
        try:
            self.few_shot_examples = [
                {
                    "input": Utility.extract_text(assess_path),
                    "output": Utility.extract_text(brd_path),
                }
                for assess_path, brd_path in zip(assessment_paths, brd_paths)
            ]
        except Exception as e:
            raise Exception(f"Error loading examples: {str(e)}")

    @staticmethod
    def _create_prompt_templates() -> tuple[PromptTemplate, PromptTemplate]:
        """Create example and main prompt templates."""
        example_prompt = PromptTemplate(
            input_variables=["input", "output"],
            template=prompts.EXAMPLE_PROMPT_TEMPLATE,
        )

        main_prompt = PromptTemplate(
            input_variables=["assessment_report", "rag_context"],
            template=prompts.MAIN_PROMPT_TEMPLATE,
        )

        return example_prompt, main_prompt

    def get_final_prompt(
        self, assessment_text: str, rag_results: Optional[str] = None
    ) -> str:
        """Generate and return the final prompt without making the API call."""
        example_prompt, main_prompt = self._create_prompt_templates()
        rag_context = (
            "No additional context available." if rag_results is None else rag_results
        )

        few_shot_prompt = FewShotPromptTemplate(
            example_prompt=example_prompt,
            examples=self.few_shot_examples,
            input_variables=["assessment_report", "rag_context"],
            prefix="Reference examples:",
            suffix=main_prompt.template.format(
                sections="\n".join(prompts.STANDARD_SECTIONS),
                assessment_report="{assessment_report}",
                rag_context="{rag_context}",
            ),
        )

        return few_shot_prompt.format(
            assessment_report=assessment_text, rag_context=rag_context
        )

    def save_prompt_to_file(self, prompt: str) -> str:
        """
        Save the prompt to a text file with timestamp.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prompt_{timestamp}.txt"
        filepath = os.path.join(self.prompts_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt)

        return filepath

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts."""
        return SequenceMatcher(None, text1, text2).ratio()

    def analyze_consistency(self, generations: List[str]) -> Dict:
        """
        Analyze consistency among generated BRDs and select the most representative one.

        Returns:
            Dict containing the most consistent BRD and consistency metrics
        """
        # Calculate pairwise similarities
        similarities = []
        for i in range(len(generations)):
            for j in range(i + 1, len(generations)):
                similarity = self.calculate_similarity(generations[i], generations[j])
                similarities.append(similarity)

        # Calculate consistency metrics
        avg_similarity = statistics.mean(similarities)
        std_similarity = statistics.stdev(similarities) if len(similarities) > 1 else 0

        # Find the most representative BRD (highest average similarity to others)
        avg_similarities = []
        for i, gen in enumerate(generations):
            other_gens = generations[:i] + generations[i + 1 :]
            avg_sim = statistics.mean(
                [self.calculate_similarity(gen, other) for other in other_gens]
            )
            avg_similarities.append(avg_sim)

        most_consistent_idx = avg_similarities.index(max(avg_similarities))

        return {
            "selected_brd": generations[most_consistent_idx],
            "average_similarity": avg_similarity,
            "similarity_std": std_similarity,
            "all_generations": generations,
        }

    def generate_single_brd(self, prompt: str, temperature: float) -> str:
        """Generate a single BRD with given temperature."""
        response = self.client.chat.complete(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": prompts.SYSTEM_MESSAGE,
                },
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        return response.choices[0].message.content

    def generate_brd(
        self,
        assessment_text: str,
        rag_results: Optional[str] = None,
        save_prompt: bool = False,
    ) -> Dict:
        """
        Generate multiple BRDs using self-consistency and select the most consistent one.

        Returns:
            Dict containing the selected BRD and consistency metrics
        """
        full_prompt = self.get_final_prompt(assessment_text, rag_results)

        if save_prompt:
            self.save_prompt_to_file(full_prompt)

        # Generate multiple BRDs with different temperatures
        temperatures = [self.temperature + (i * 0.1) for i in range(self.num_samples)]

        # Use ThreadPoolExecutor for parallel generation
        with ThreadPoolExecutor(max_workers=self.num_samples) as executor:
            generations = list(
                executor.map(
                    lambda temp: self.generate_single_brd(full_prompt, temp),
                    temperatures,
                )
            )

        # Analyze consistency and select the best BRD
        consistency_results = self.analyze_consistency(generations)

        return consistency_results


if __name__ == "__main__":
    brd_generator = BRDGenerator(
        api_key=os.getenv("MISTRAL_API"), model="mistral-large-latest"
    )
    # Populate rag_results with a list of strings
    rag_results = [
        "Additional context from similar projects...",
        "More additional context...",
    ]
    brd_initial_content = brd_generator.generate_brd(
        "This is a test assessment", rag_results=rag_results, save_prompt=True
    )
    # print("brd generated", brd_initial_content["selected_brd"])
    print("brd generated")
