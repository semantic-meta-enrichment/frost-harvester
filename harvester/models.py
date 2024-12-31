from typing import Optional, Dict, List, Any
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

model_config = ConfigDict(
    alias_generator=to_camel,
    populate_by_name=True,
    from_attributes=True,
)


class CommonFields(BaseModel):
    """Base mixin for common fields for relevant SensorThings API Entities"""
    model_config = model_config
    id: int = Field(alias="@iot.id")
    name: str
    description: str
    properties: Optional[Dict[str, Any]] = None


class Sensor(CommonFields):
    encoding_type: str


class ObservedProperty(CommonFields):
    pass


class Datastream(CommonFields):
    unit_of_measurement: Dict
    observed_area: Optional[Dict] = None
    phenomenon_time: Optional[str] = None
    result_time: Optional[str] = None
    sensor: Sensor = Field(alias="Sensor")
    observed_property: Optional[ObservedProperty] = Field(
        default=None, alias="ObservedProperty")


class Thing(CommonFields):
    datastreams: List[Datastream] = Field(alias="Datastreams")

    def __str__(self):
        return self.model_dump_json(by_alias=True, exclude_none=True)
