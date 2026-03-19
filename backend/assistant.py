"""
Handles the creation, retrieval, and configuration of the OpenAI Assistant.

This module ensures that a single, consistent Assistant is used for the application,
persisting its ID to avoid creating duplicates on server restarts.
"""

import json
import logging
import os
from pathlib import Path

from openai import OpenAI
from openai.types.beta import Assistant

# Import the synchronous client getter
from openai_client import get_client

logger = logging.getLogger(__name__)

# Define the path to store the assistant ID, and the assistant's configuration
ASSISTANT_FILE_PATH = Path(__file__).parent / "assistant.json"
ASSISTANT_NAME = "CISAT Academic Advisor"
ASSISTANT_INSTRUCTIONS = """
You are an expert academic advisor for Claremont Graduate University's Center for Information Systems & Technology (CISAT).
Your role is to provide accurate, helpful, and safe guidance to students based on their uploaded graduation plan and the official documents you have access to.

1.  **Analyze Graduation Plans**: When a student uploads a PDF, CSV, or other document, you MUST use the 'file_search' tool to meticulously analyze its content. Compare the student's completed and planned courses against the official degree requirements.
2.  **Identify Gaps**: Identify any missing requirements, incorrect course sequences, or potential issues based on the documents.
3.  **Trigger UI Navigation**: If you identify a gap or an area for recommendations, you MUST use the `trigger_ui_navigation` tool to guide the student to the correct screen in the web application (e.g., 'GapAnalysis', 'Recommendations'). Be specific in the data you extract.
4.  **Escalate When Necessary**: If a student's plan has a critical issue that requires human intervention (e.g., risk of not graduating on time), you MUST use the `email_supervisor` tool. Provide a clear, concise summary of the issue and set an appropriate urgency level.
5.  **Be Professional and Cautious**: Always maintain a professional and encouraging tone. Do not provide information outside of your knowledge base. If you cannot answer a question from the provided documents, state that clearly. Do not make up answers.
"""

# Define the tools the assistant can use, including custom functions and file_search
ASSISTANT_TOOLS: list[dict] = [
    {"type": "file_search"},
    {
        "type": "function",
        "function": {
            "name": "trigger_ui_navigation",
            "description": "Navigates the user to a specific screen in the frontend application to show relevant information discovered from their documents or conversation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "target_route": {
                        "type": "string",
                        "description": "The name of the screen to navigate to.",
                        "enum": [
                            "GapAnalysis",
                            "Recommendations",
                            "CourseHistory",
                            "AdvisorConfirmation",
                        ],
                    },
                    "extracted_data": {
                        "type": "object",
                        "description": "A JSON object containing any data needed by the target screen, extracted from the user's plan or conversation. For example, a list of missing courses for GapAnalysis.",
                    },
                },
                "required": ["target_route"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "email_supervisor",
            "description": "Escalates a critical student issue to a human academic supervisor via email. Use this for issues that cannot be resolved by the student alone.",
            "parameters": {
                "type": "object",
                "properties": {
                    "student_id": {
                        "type": "string",
                        "description": "The student's ID, if available in the conversation or documents.",
                    },
                    "issue_summary": {
                        "type": "string",
                        "description": "A concise, one-to-two sentence summary of the critical issue for the supervisor.",
                    },
                    "urgency_level": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                        "description": "The assessed urgency of the issue.",
                    },
                },
                "required": ["issue_summary", "urgency_level"],
            },
        },
    },
]


def get_or_create_assistant() -> Assistant:
    """
    Retrieves the existing OpenAI Assistant ID or creates a new one.

    Checks for an environment variable, then a local file. If not found,
    it creates a new assistant with the defined tools and instructions
    and saves the ID.
    """
    client = get_client()  # Use the synchronous client for this setup task
    assistant_id = os.environ.get("OPENAI_ASSISTANT_ID")

    # 1. Check environment variable
    if assistant_id:
        logger.info(f"Found assistant ID in environment variable: {assistant_id}")
        try:
            assistant = client.beta.assistants.retrieve(assistant_id)
            logger.info("Successfully retrieved assistant from OpenAI.")
            return assistant
        except Exception as e:
            logger.error(
                f"Could not retrieve assistant {assistant_id} from OpenAI. "
                f"Please check if the ID is correct and has been deleted. Error: {e}",
            )
            # Fall through to create a new one
            pass

    # 2. Check local file
    if ASSISTANT_FILE_PATH.exists():
        with open(ASSISTANT_FILE_PATH, "r") as f:
            try:
                data = json.load(f)
                assistant_id = data.get("assistant_id")
                if assistant_id:
                    logger.info(f"Loaded assistant ID from file: {assistant_id}")
                    try:
                        assistant = client.beta.assistants.retrieve(assistant_id)
                        logger.info("Successfully retrieved assistant from OpenAI.")
                        # Optional: Store in env var for subsequent calls
                        os.environ["OPENAI_ASSISTANT_ID"] = assistant.id
                        return assistant
                    except Exception as e:
                        logger.warning(
                            f"Failed to retrieve assistant {assistant_id} from file, will create a new one. Error: {e}"
                        )
            except json.JSONDecodeError:
                logger.warning(
                    f"Could not decode JSON from {ASSISTANT_FILE_PATH.name}. A new assistant will be created."
                )

    # 3. Create a new assistant if not found
    logger.info("No valid assistant found, creating a new one...")
    assistant = client.beta.assistants.create(
        name=ASSISTANT_NAME,
        instructions=ASSISTANT_INSTRUCTIONS,
        model="gpt-4o-mini",  # Or another preferred model
        tools=ASSISTANT_TOOLS,
    )

    # Save the new assistant's ID for persistence
    with open(ASSISTANT_FILE_PATH, "w") as f:
        json.dump({"assistant_id": assistant.id}, f)

    # Set the env var for the current process
    os.environ["OPENAI_ASSISTANT_ID"] = assistant.id

    logger.info(f"New assistant created and saved with ID: {assistant.id}")
    return assistant
