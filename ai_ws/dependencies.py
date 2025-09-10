from functools import lru_cache
from .agent import runnable


@lru_cache(maxsize=1)
def get_agent_runnable():
    """
    Returns a cached instance of the LangGraph agent.
    Using lru_cache ensures the agent graph is compiled only once.
    """
    return runnable
