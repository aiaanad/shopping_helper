from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_serializer


class BaseSchema(BaseModel):
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    model_config = ConfigDict(
        from_attributes=True,
        validate_by_name=True,
        validate_by_alias=True,
    )

    @field_serializer('created_at', 'updated_at')
    def serialize_datetime(self, dt: datetime, _info):
        return dt.isoformat()
