from enum import Enum

class LocationType(Enum):
    STATE = "STATE", "State"
    CITY = "CITY", "City"
    ZIPCODE = "ZIPCODE", "Zipcode"
    COUNTY = "COUNTY", "County"
    COUNTRY = "COUNTRY", "Country"
    FULL_ADDRESS = "FULL_ADDRESS", "Full Address"

    @classmethod
    def choices(cls):
        return [(key.value[0], key.value[1]) for key in cls]

class SharingType(Enum):
    OPEN = "OPEN", "Public"
    CLOSED = "CLOSED", "Private"
    OPEN_TO = "OPEN_TO", "Open to"
    CLOSED_TO = "CLOSED_TO", "Closed to"

    @classmethod
    def choices(cls):
        return [(key.value[0], key.value[0]) for key in cls]
