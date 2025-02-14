import typing

from fastavro.validation import validate

from .schema_generator import CT, AvroModel, JsonDict

try:
    from pydantic import BaseModel  # pragma: no cover
except ImportError as ex:  # pragma: no cover
    raise Exception("pydantic must be installed in order to use AvroBaseModel") from ex  # pragma: no cover


class AvroBaseModel(BaseModel, AvroModel):
    @classmethod
    def json_schema(cls, *args, **kwargs) -> str:
        return cls.schema_json(*args, **kwargs)

    def asdict(self) -> JsonDict:
        """
        Document this. asdict vs dict
        """
        data = self.dict()

        # te standardize called can be replaced if we have a custom implementation of asdict
        # for now I think is better to use the native implementation
        return {key: self.standardize_custom_type(value) for key, value in data.items()}

    def validate_avro(self) -> bool:
        """
        Document this!!!
        """
        schema = self.avro_schema_to_python()
        return validate(self.asdict(), schema)

    @classmethod
    def parse_obj(cls, data: typing.Dict) -> typing.Union[JsonDict, CT]:
        return super().parse_obj(data)
