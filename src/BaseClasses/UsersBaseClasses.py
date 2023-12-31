"""Actors"""
from typing import List, Optional

from pydantic import Field, model_validator, BaseModel, constr

from src.BaseClasses.BaseClasses import CoreModel, FirestoreIDType
from src.logger import setup_logger

logger = setup_logger(__name__)


class InputAppUser(BaseModel):
    # Better validator for email
    email: constr(min_length=2, max_length=50, strip_whitespace=True)
    password: str = None
    display_name: str = None
    phone_number: str = None
    photo_url: str = None
    email_verified: bool = None


class OuputAppUser(BaseModel):
    uid: str = Field(None, hidden=True)
    email: str = None
    display_name: str = None
    phone_number: str = None
    photo_url: str = None
    email_verified: bool = None


class Actor(CoreModel):
    uid: str
    phone_number: str  # Phone number is used as the ID.
    first_name: str
    last_name: str

    # # Optional for now (perhaps they get autofilled by the system based on other data)
    # #   Contact Info
    # email: Optional[str]
    # #  Personal Info
    # age: Optional[int]
    # height: Optional[float]
    # weight: Optional[float]
    # # Automatically Generated if not provided
    # joined_date: date = date.today()

    @model_validator(mode="before")
    def set_id(cls, values):
        values["id"] = FirestoreIDType(value=f'{values["uid"]}')
        return values


class Player(Actor):
    teams: List[FirestoreIDType] = []  # Team ID.


class Admin(Actor):
    permissions: List[FirestoreIDType]


class Employee(Actor):
    actor_description: str
    supervisor: Optional[FirestoreIDType]  # Link to another Employee or Admin ID.


class Referee(Actor):
    assigned_games: List[FirestoreIDType]  # List of Game IDs.
    games_officiated: List[FirestoreIDType]
    yellow_cards_given: int
    performance_rating: float


class Coach(Actor):
    coaching_style: str
    years_of_experience: int
