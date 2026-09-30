from pydantic import BaseModel, Field


class SessionCreate(BaseModel):
    route: str = Field(min_length=3)
    driver: str = Field(min_length=2)
    capacity: int = Field(gt=0)
    departure_time: str
    status: str = "Available"


class SessionOut(BaseModel):
    id: int
    route: str
    driver: str
    capacity: int
    departure_time: str
    status: str
