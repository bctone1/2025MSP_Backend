from pydantic import BaseModel
from typing import Literal, Optional

class VSCodeCommand(BaseModel):
    action: Literal["open_file", "run_command", "close_vscode"]
    filename: Optional[str] = None
    command: Optional[str] = None