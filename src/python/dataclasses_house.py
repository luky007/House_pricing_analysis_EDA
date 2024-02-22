"""Represents the data structures as defined in the ER model."""
from dataclasses import dataclass


@dataclass
class HousePriceData:
    """Define the house_price_data table."""

    house_id: int
    area: int | None = None
    price: int | None = None


@dataclass
class HouseData:
    """Define the House_data table."""

    house_id: int
    n_bedroom: int | None = None
    n_bathroom: int | None = None
    n_stories: int | None = None
    n_parking_slot: int | None = None
    is_mainroad: bool | None = None
    has_guestroom: bool | None = None
    has_basement: bool | None = None
    has_hot_water: bool | None = None
    has_air_conditioning: bool | None = None
    is_pref_area: bool | None = None
    furnishing_id: int | None = None
