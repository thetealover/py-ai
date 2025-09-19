import importlib.metadata


def get_project_version() -> str:
    return importlib.metadata.version("py-ai")
