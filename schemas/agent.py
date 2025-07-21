from pydantic import BaseModel
from typing import List
from datetime import datetime

class WriteAgentStep2Request(BaseModel):
    message : str
    provider : str
    model : str
    api_key : str
