# models.py
from pydantic import BaseModel
from typing import List

class RouteQuery(BaseModel):
    start: str
    end: str

class RouteSuggestion(BaseModel):
    status: str
    main_route: List[str]
    main_eta: float
    best_route: List[str]
    best_eta: float
