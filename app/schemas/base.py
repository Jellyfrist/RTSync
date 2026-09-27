from pydantic import BaseModel, ConfigDict


class ResponseModel(BaseModel):
    """Serialize domain objects without coupling them to the HTTP layer."""

    model_config = ConfigDict(from_attributes=True)
