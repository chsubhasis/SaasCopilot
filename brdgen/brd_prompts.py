SYSTEM_MESSAGE = (
    "You are a business analyst working on a project to create a "
    "detail Business Requirements Document (BRD) for a new software application. "
    "You have been provided with an assessment report and additional context. "
    "Use this information to generate a BRD."
)

EXAMPLE_PROMPT_TEMPLATE = "Assessment:\n{input}\n\nBRD:\n{output}"

MAIN_PROMPT_TEMPLATE = """
Generate detail BRD based on below details.

Guidelines:
- Clear, professional language
- Reference assessment report
- Thorough section coverage
- Follow example structure
- Specific, measurable requirements

Sections:
{sections}

Assessment:
{assessment_report}

Additional Context from Similar Projects:
{rag_context}

Use the additional context to enhance the BRD while maintaining focus on the current project requirements.

Generate BRD:
"""

# For saving prompts
PROMPT_FILE_PREFIX = "prompt_"
PROMPT_TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"

STANDARD_SECTIONS = [
    "1. Executive Summary",
    "2. Project Scope",
    "3. Business Requirements",
    "4. Functional Requirements",
    "5. Non-Functional Requirements",
    "6. Constraints and Assumptions",
    "7. Stakeholder Requirements",
    "8. High-Level Solution Architecture",
    "9. Risk Analysis",
    "10. Acceptance Criteria",
]
