from enum import Enum

class LocationType(Enum):
    DRINKING_AREA = {
        "amenity": ["bar", "biergarten", "pub", "casino", "nightclub", "gambling"]
    }
    BUS_STOP = {
        "highway": ["bus_stop"]
    }
    GENERAL_AMENITY = {
        "amenity":["dentist", "doctors", "hospital", "clinic", "cinema", "library", "community_centre", "place_of_worship", "school", "cafe"],
        "leisure":["playground"],
        "tourism":["artwork"]
    }