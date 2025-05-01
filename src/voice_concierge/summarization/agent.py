# src/voice_concierge/summarization/agent.py
from typing import Optional

from agents import Agent
from voice_concierge.utils.logging_utils import get_logger
from voice_concierge.retrieval.retrieval_agent import create_retrieval_agent

logger = get_logger(__name__)


def create_summarizer_agent(retrieval_agent: Optional[Agent] = None) -> Agent:
    """Create and configure the summarizer agent.

    Args:
        retrieval_agent: Optional retrieval agent to use. If not provided, a new one will be created.

    Returns:
        Configured summarizer agent.
    """
    if retrieval_agent is None:
        retrieval_agent = create_retrieval_agent()

    system_message = """You are an executive-level note-taker and summarizer.
    Your task is to convert meeting transcripts into concise, well-organized bullet points.

    Follow these guidelines:
    - Group information by topic or theme
    - Use at most 5 bullets per topic
    - Prefix each bullet point with •
    - When attendees mention a policy or document, include relevant context from the knowledge base
    - Always cite the filename when including information from documents
    - Focus on key decisions, action items, and important discussions
    - Maintain a professional, objective tone suitable for executives
    - Organize information in a logical flow"""

    logger.info("Creating summarizer agent")

    # Create the agent with the retrieval agent as a tool
    agent = Agent(
        name="Summarizer",
        llm="o3",
        system_message=system_message,
        tools=[retrieval_agent],
        return_format="json_object",
    )

    return agent
