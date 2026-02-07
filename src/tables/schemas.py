from pydantic import BaseModel, ConfigDict, Field


class TableRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    seats: int


class TableCreate(BaseModel):
    name: str = Field(examples=["Table 1"])
    seats: int = Field(examples=[2])


class TableUpdate(BaseModel):
    name: str | None = Field(default=None, examples=["Table 12"])
    seats: int | None = Field(default=None, examples=[6])
