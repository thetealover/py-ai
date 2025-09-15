from fastapi import Request, Depends
from src.ai.agents.chat_agent import ChatAgent
from src.ai.agent_manager import AgentManager
from src.api.services.chat_service import ChatService


def get_agent_manager(request: Request) -> AgentManager:
    """Dependency to get the agent manager from the app state."""
    return request.app.state.agent_manager


def get_agent(
        manager: AgentManager = Depends(get_agent_manager)
) -> ChatAgent:
    """
    Dependency to get the single, persistent agent instance
    from the agent manager.
    """
    return manager.get_agent()


def get_chat_service(
        agent: ChatAgent = Depends(get_agent)
) -> ChatService:
    """Dependency to get the chat service instance."""
    return ChatService(agent)
