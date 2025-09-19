import logging
from typing import List

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.ai.prompts import TITLE_GENERATION_PROMPT
from src.api.db import save_conversation_title, check_conversation_title_exists
from src.config.settings import settings

logger = logging.getLogger(__name__)

title_generation_model = ChatGoogleGenerativeAI(
    model=settings.title_determinator_llm_model,
    temperature=settings.title_determinator_llm_temperature,
    google_api_key=settings.google_api_key,
)


async def generate_and_save_title(thread_id: str, history: List[BaseMessage]):
    """
    Generates a title for a conversation if it doesn't already have one
    and saves it to the database.
    """
    try:
        if await check_conversation_title_exists(thread_id):
            return

        formatted_history = "\n".join(
            f"{'User' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}"
            for msg in history
            if isinstance(msg, (HumanMessage, AIMessage))
        )

        if not formatted_history:
            return

        prompt = TITLE_GENERATION_PROMPT.format(conversation_history=formatted_history)
        response = await title_generation_model.ainvoke(prompt)
        title = response.content.strip().strip('"')

        if title:
            await save_conversation_title(thread_id, title)
            logger.info(
                f"Generated and saved title for thread '{thread_id}': '{title}'"
            )

    except Exception as e:
        logger.error(f"Error generating title for thread {thread_id}: {e}")
