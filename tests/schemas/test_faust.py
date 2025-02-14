import dataclasses
import datetime
import enum
import json
import typing
import uuid

import faust

from dataclasses_avroschema import AvroModel, types, utils

encoded = "test".encode()


def test_faust_record_schema_primitive_types(user_avro_json):
    class User(faust.Record, AvroModel):
        name: str
        age: int
        has_pets: bool
        money: float
        encoded: bytes

        class Meta:
            schema_doc = False

    assert User.avro_schema() == json.dumps(user_avro_json)


def test_faust_record_schema_complex_types(user_advance_avro_json, color_enum):
    class UserAdvance(faust.Record, AvroModel):
        name: str
        age: int
        pets: typing.List[str]
        accounts: typing.Dict[str, int]
        favorite_colors: color_enum
        has_car: bool = False
        country: str = "Argentina"
        address: str = None
        md5: types.Fixed = types.Fixed(16)

        class Meta:
            schema_doc = False

    assert UserAdvance.avro_schema() == json.dumps(user_advance_avro_json)


def test_faust_record_schema_complex_types_with_defaults(user_advance_with_defaults_avro_json, color_enum):
    class UserAdvance(faust.Record, AvroModel):
        name: str
        age: int
        pets: typing.List[str] = dataclasses.field(default_factory=lambda: ["dog", "cat"])
        accounts: typing.Dict[str, int] = dataclasses.field(default_factory=lambda: {"key": 1})
        has_car: bool = False
        favorite_colors: color_enum = color_enum.BLUE
        country: str = "Argentina"
        address: str = None

        class Meta:
            schema_doc = False

    assert UserAdvance.avro_schema() == json.dumps(user_advance_with_defaults_avro_json)


def test_faust_record_schema_logical_types(logical_types_schema):
    a_datetime = datetime.datetime(2019, 10, 12, 17, 57, 42)

    class LogicalTypes(faust.Record, AvroModel):
        "Some logical types"
        birthday: datetime.date = a_datetime.date()
        meeting_time: datetime.time = a_datetime.time()
        release_datetime: datetime.datetime = a_datetime
        event_uuid: uuid.uuid4 = "09f00184-7721-4266-a955-21048a5cc235"

    assert LogicalTypes.avro_schema() == json.dumps(logical_types_schema)


def test_faust_record_one_to_one_relationship(user_one_address_schema):
    """
    Test schema relationship one-to-one
    """

    class Address(faust.Record, AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record, AvroModel):
        "An User with Address"
        name: str
        age: int
        address: Address

    assert User.avro_schema() == json.dumps(user_one_address_schema)


def test_faust_record_one_to_one_relationship_with_none_default(user_one_address_schema_with_none_default):
    """
    Test schema relationship one-to-one
    """

    class Address(faust.Record, AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record, AvroModel):
        "An User with Address"
        name: str
        age: int
        address: Address = None

    assert User.avro_schema() == json.dumps(user_one_address_schema_with_none_default)


def test_faust_record_one_to_many_relationship(user_many_address_schema):
    """
    Test schema relationship one-to-many
    """

    class Address(faust.Record, AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record, AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.List[Address]

    assert User.avro_schema() == json.dumps(user_many_address_schema)


def test_faust_record_one_to_many_map_relationship(user_many_address_map_schema):
    """
    Test schema relationship one-to-many using a map
    """

    class Address(faust.Record, AvroModel):
        "An Address"
        street: str
        street_number: int

    class User(faust.Record, AvroModel):
        "User with multiple Address"
        name: str
        age: int
        addresses: typing.Dict[str, Address]

    assert User.avro_schema() == json.dumps(user_many_address_map_schema)


def test_faust_record_self_one_to_one_relationship(user_self_reference_one_to_one_schema):
    """
    Test self relationship one-to-one
    """

    class User(faust.Record, AvroModel):
        "User with self reference as friend"
        name: str
        age: int
        friend: typing.Type["User"]
        teamates: typing.Type["User"] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_one_schema)


def test_faust_record_self_one_to_many_relationship(
    user_self_reference_one_to_many_schema,
):
    """
    Test self relationship one-to-many
    """

    class User(faust.Record, AvroModel):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.List[typing.Type["User"]]
        teamates: typing.List[typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_schema)


def test_faust_record_self_one_to_many_map_relationship(
    user_self_reference_one_to_many_map_schema,
):
    """
    Test self relationship one-to-many Map
    """

    class User(faust.Record, AvroModel):
        "User with self reference as friends"
        name: str
        age: int
        friends: typing.Dict[str, typing.Type["User"]]
        teamates: typing.Dict[str, typing.Type["User"]] = None

    assert User.avro_schema() == json.dumps(user_self_reference_one_to_many_map_schema)


def test_faust_record_schema_with_unions_type(union_type_schema):
    class Bus(faust.Record, AvroModel):
        "A Bus"
        engine_name: str

        class Meta:
            namespace = "types.bus_type"

    class Car(faust.Record, AvroModel):
        "A Car"
        engine_name: str

        class Meta:
            namespace = "types.car_type"

    class TripDistance(enum.Enum):
        CLOSE = "Close"
        FAR = "Far"

        class Meta:
            doc = "Distance of the trip"

    class UnionSchema(faust.Record, AvroModel):
        "Some Unions"
        first_union: typing.Union[str, int]
        logical_union: typing.Union[datetime.datetime, datetime.date, uuid.uuid4]
        lake_trip: typing.Union[Bus, Car]
        river_trip: typing.Union[Bus, Car] = None
        mountain_trip: typing.Union[Bus, Car] = dataclasses.field(default_factory=lambda: {"engine_name": "honda"})
        trip_distance: typing.Union[int, TripDistance] = None

    assert UnionSchema.avro_schema() == json.dumps(union_type_schema)


def test_not_faust_not_installed(monkeypatch):
    monkeypatch.setattr(utils, "faust", None)

    class Bus:
        pass

    assert not utils.is_faust_model(Bus)
