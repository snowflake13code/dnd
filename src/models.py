from pydantic import BaseModel
from typing import Literal, Optional

class QueryRoute(BaseModel):
    route: Literal["story", "session", "arc"]
    session: Optional[int] = None
    arc: Optional[int] = None