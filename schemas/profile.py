"""
User profile schema - universal across all assistant types.
"""

from typing import Optional
from pydantic import BaseModel, Field


class Profile(BaseModel):
    """
    Universal user profile schema.
    
    Stores general information about the user that persists
    across all assistant types.
    """
    
    name: Optional[str] = Field(
        description="The user's name",
        default=None
    )
    
    location: Optional[str] = Field(
        description="The user's location",
        default=None
    )
    
    job: Optional[str] = Field(
        description="The user's job or occupation",
        default=None
    )
    
    connections: list[str] = Field(
        description="Personal connections of the user, such as family members, friends, or coworkers",
        default_factory=list
    )
    
    interests: list[str] = Field(
        description="Interests and hobbies that the user has",
        default_factory=list
    )
