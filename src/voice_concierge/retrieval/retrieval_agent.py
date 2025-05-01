# src/voice_concierge/retrieval/retrieval_agent.py
from typing import List, Dict, Any, Optional

from agents import Agent, Tool
from voice_concierge.config import settings
from voice_concierge.utils.logging_utils import get_logger
from voice_concierge.retrieval.vector_store import get_vector_store

logger = get_logger(__name__)


class FileSearchTool(Tool):
    """Tool for searching documents in the vector store."""

    name = "file_search"
    description = "Search for relevant information in the document corpus."

    def __init__(self, vector_store_path: Optional[str] = None):
        """Initialize the file search tool.

        Args:
            vector_store_path: Path to the vector store. Defaults to config setting.
        """
        self.vector_store_path = vector_store_path or settings.vector_store_path
        self.vector_store = get_vector_store(self.vector_store_path)
        logger.info(f"Initialized FileSearchTool with store: {self.vector_store_path}")

    def run(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for documents relevant to the query.

        Args:
            query: The search query.
            top_k: Number of results to return.

        Returns:
            List of documents with their content and metadata.
        """
        logger.info(f"Searching for: '{query}' (top_k={top_k})")
        try:
            results = self.vector_store.search(query, top_k=top_k)
            logger.debug(f"Found {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Error searching vector store: {str(e)}")
            raise


def create_retrieval_agent() -> Agent:
    """Create and configure the retrieval agent.

    Returns:
        Configured retrieval agent.
    """
    system_message = """You are a retrieval agent for a document corpus.
    Answer queries only using information from the supplied context.
    Always cite the filename source for any information you provide.
    If you don't know the answer, say so clearly rather than speculating.
    Format your responses in markdown for readability."""

    logger.info("Creating retrieval agent")

    # Create the agent with the file search tool
    agent = Agent(
        name="DocumentRetriever",
        llm="o3",
        system_message=system_message,
        tools=[FileSearchTool()],
    )

    return agent
