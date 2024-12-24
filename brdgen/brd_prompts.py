SYSTEM_MESSAGE = (
    "You are a business analyst working on a project to create a "
    "detail Business Requirements Document (BRD) for a new software application. "
    "You have been provided with an assessment report and additional context. "
    "Use this information to generate a BRD."
)

EXAMPLE_PROMPT_TEMPLATE = "Sample Assessment Report:{input} \n Corresponding Sample Business Requirements Document:{output}"

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

REFINE_BRD_PROMPT_SYSTEM = """
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
"""
