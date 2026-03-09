import pytest
from tests.load_module import load_module

validate_coordinates = load_module("server/app/domain/routing/validate_coordinates.py")
validate_coordinates = validate_coordinates.validate_coordinates

# Valid formats
def test_valid_tuple():
    assert validate_coordinates((51.5, -2.6)) is True

def test_valid_list():
    assert validate_coordinates([51.5, -2.6]) is True

def test_valid_dict():
    assert validate_coordinates({"lat": 51.5, "lon": -2.6}) is True

def test_valid_string():
    assert validate_coordinates("51.5,-2.6") is True

def test_valid_string_with_spaces():
    assert validate_coordinates(" 51.5 ,  -2.6 ") is True

# Invalid formats
def test_invalid_dict_missing_keys():
    assert validate_coordinates({"latitude": 51.5, "longitude": -2.6}) is False

def test_invalid_string_no_comma():
    assert validate_coordinates("51.5 -2.6") is False

def test_invalid_string_too_many_parts():
    assert validate_coordinates("51.5,-2.6,10") is False

def test_invalid_type():
    assert validate_coordinates(12345) is False
    assert validate_coordinates(None) is False

def test_invalid_list_length():
    assert validate_coordinates([51.5]) is False
    assert validate_coordinates([51.5, -2.6, 10]) is False

# Numeric conversion failures
def test_invalid_non_numeric_values():
    assert validate_coordinates(("abc", "def")) is False
    assert validate_coordinates({"lat": "north", "lon": "west"}) is False

# Bounds checking
def test_latitude_out_of_bounds():
    assert validate_coordinates((100, 0)) is False
    assert validate_coordinates((-100, 0)) is False

def test_longitude_out_of_bounds():
    assert validate_coordinates((0, 200)) is False
    assert validate_coordinates((0, -200)) is False

def test_boundary_values():
    assert validate_coordinates((90, 180)) is True
    assert validate_coordinates((-90, -180)) is True