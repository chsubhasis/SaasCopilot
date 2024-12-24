from typing import List, Optional, Dict, Tuple
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
from dataclasses import dataclass

load_dotenv()


@dataclass
class ConsistencyMetrics:
    """Data class for storing BRD consistency analysis results."""

    selected_brd: str
    average_similarity: float
    similarity_std: float
    all_generations: List[str]


class BRDGenerator:
    """
    Business Requirements Document (BRD) generator using the Mistral API.

    This class handles the generation of BRDs from assessment reports using few-shot learning
    and self-consistency checking.
    """

    def __init__(
        self,
        api_key: str,
        model: str,
        temperature: float = 0.3,
        num_samples: int = 2,
        similarity_threshold: float = 0.8,
        example_assessment_paths: Optional[List[str]] = None,
        example_brd_paths: Optional[List[str]] = None,
    ) -> None:
        """
        Initialize the BRD generator.

        Args:
            api_key: Mistral API key
            model: Name of the Mistral model to use
            temperature: Generation temperature (default: 0.3)
            num_samples: Number of samples for self-consistency (default: 2)
            similarity_threshold: Threshold for consistency checking (default: 0.8)
            example_assessment_paths: Paths to example assessment files
            example_brd_paths: Paths to example BRD files
        """
        if not api_key:
            raise ValueError("API key is required")

        self.client = Mistral(api_key=api_key)
        self.model = model
        self.temperature = temperature
        self.few_shot_examples = []
        self.num_samples = num_samples
        self.similarity_threshold = similarity_threshold
        self.prompts_dir = os.path.join(os.getcwd(), "prompts")
        os.makedirs(self.prompts_dir, exist_ok=True)

        if example_assessment_paths and example_brd_paths:
            self.load_examples(example_assessment_paths, example_brd_paths)

    # TODO - verify if the assessment and BRD files are at all needed to inject within prompt
    # This will increase the size of the prompt and may not be necessary
    # Making this optional for now
    def load_examples(self, assessment_paths: List[str], brd_paths: List[str]) -> None:
        """Load example assessments and BRDs for few-shot learning."""
        print("Loading examples...")
        try:
            examples = []
            for assess_path, brd_path in zip(assessment_paths, brd_paths):
                if not os.path.exists(assess_path):
                    raise FileNotFoundError(f"Assessment file not found: {assess_path}")
                if not os.path.exists(brd_path):
                    raise FileNotFoundError(f"BRD file not found: {brd_path}")

                example = {
                    "input": Utility.extract_text(assess_path),
                    "output": Utility.extract_text(brd_path),
                }
                examples.append(example)
            self.few_shot_examples = examples
        except Exception as e:
            raise RuntimeError(f"Failed to load examples: {str(e)}")

    @staticmethod
    def _create_prompt_templates() -> Tuple[PromptTemplate, PromptTemplate]:
        """Create example and main prompt templates."""
        print("Creating prompt templates...")
        return (
            PromptTemplate(
                input_variables=["input", "output"],
                template=prompts.EXAMPLE_PROMPT_TEMPLATE,
            ),
            PromptTemplate(
                input_variables=["sections", "assessment_report", "rag_context"],
                template=prompts.MAIN_PROMPT_TEMPLATE,
            ),
        )

    def get_final_prompt(
        self, assessment_text: str, rag_results: Optional[str] = None
    ) -> str:
        """
        Generate the final prompt for BRD generation.

        Args:
            assessment_text: Input assessment text
            rag_results: Optional RAG context

        Returns:
            Formatted prompt string
        """
        print("Creating final prompt...")
        example_prompt, main_prompt = self._create_prompt_templates()
        rag_context = rag_results or "No additional context available."

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
        """Save the prompt to a timestamped file."""
        print("Saving prompt to file...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"prompt_{timestamp}.txt"
        filepath = os.path.join(self.prompts_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(prompt)

        return filepath

    def calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity ratio between two texts."""
        return SequenceMatcher(None, text1, text2).ratio()

    def analyze_consistency(self, generations: List[str]) -> ConsistencyMetrics:
        """
        Analyze consistency among generated BRDs and select the most representative one.

        Returns:
            Dict containing the most consistent BRD and consistency metrics
        """
        print("Analyzing consistency...")
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
        print("avg_similarities", avg_similarities)
        most_consistent_idx = avg_similarities.index(max(avg_similarities))

        return ConsistencyMetrics(
            selected_brd=generations[most_consistent_idx],
            average_similarity=avg_similarity,
            similarity_std=std_similarity,
            all_generations=generations,
        )

    def generate_single_brd(self, prompt: str, temperature: float) -> str:
        """Generate a single BRD with given temperature."""
        print(f"Generating single BRD with temperature {temperature}...")
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompts.SYSTEM_MESSAGE},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
            )
            return response.choices[0].message.content
        except Exception as e:
            raise RuntimeError(f"Failed to generate BRD: {str(e)}")

    def generate_brd(
        self,
        assessment_text: str,
        rag_results: Optional[str] = None,
        save_prompt: bool = False,
    ) -> ConsistencyMetrics:
        """
        Generate multiple BRDs and select the most consistent one.

        Args:
            assessment_text: Input assessment text
            rag_results: Optional RAG context
            save_prompt: Whether to save the prompt to file

        Returns:
            ConsistencyMetrics containing the selected BRD and metrics
        """
        print("Generating BRD...")
        if not assessment_text:
            raise ValueError("Assessment text cannot be empty")

        full_prompt = self.get_final_prompt(assessment_text, rag_results)

        if save_prompt:
            self.save_prompt_to_file(full_prompt)

        temperatures = [self.temperature + (i * 0.1) for i in range(self.num_samples)]

        with ThreadPoolExecutor(max_workers=self.num_samples) as executor:
            generations = list(
                executor.map(
                    lambda temp: self.generate_single_brd(full_prompt, temp),
                    temperatures,
                )
            )
        return self.analyze_consistency(generations)


"""	
# Below is the main function to demonstrate BRD generation
if __name__ == "__main__":
    #Main function to demonstrate BRD generation.
    # example_assessments = ["examples/assessment_1.pdf", "examples/assessment_2.pdf"]
    # example_brds = ["examples/brd_1.docx", "examples/brd_2.docx"]
    example_assessments = []
    example_brds = []

    try:
        brd_generator = BRDGenerator(
            api_key=os.getenv("MISTRAL_API"),
            model="mistral-large-latest",
            # example_assessment_paths=example_assessments,
            # example_brd_paths=example_brds,
        )

        rag_results = [
            "Additional context from similar projects...",
            "More additional context...",
        ]

        result = brd_generator.generate_brd(
            assessment_text="Input assessment text...",  # TODO - replace with actual assessment text
            rag_results="\n".join(rag_results),
            save_prompt=True,
        )
        print(f"BRD generated with average similarity: {result.average_similarity:.2f}")

    except Exception as e:
        print(f"Error generating BRD: {str(e)}")
"""
