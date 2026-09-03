from pathlib import Path
from fastapi.templating import Jinja2Templates
from fastapi import Request


def get_templates() -> Jinja2Templates:
    current_file = Path(__file__).resolve()

    for parent in current_file.parents:
        templates_dir = parent / "frontend" / "templates"
        if templates_dir.exists() and templates_dir.is_dir():
            templates = Jinja2Templates(directory=str(templates_dir))

            def get_flashed_messages_stub():
                return []

            templates.env.globals["get_flashed_messages"] = get_flashed_messages_stub
            return templates

    raise RuntimeError("templates directory not found")
