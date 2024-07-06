from pydantic import BaseModel, Field
from datetime import date as Date, time as Time, datetime as Datetime
from typing import Optional

from dataclasses import dataclass, field
import pandas as pd

from .inputs import GPTV_SCORER, scorer_registry
# Must inherent from Base Model
@scorer_registry.register("opentable")
class GPTV_OPENTABLE_SCORER(GPTV_SCORER, BaseModel):
  # inheritd from GPTV_SCORER
    # is_task_completed: bool 
    # score: float
    # explanation: str
  score: Optional[float] = Field(..., description="a score between 0 and 1 on the best estimated progress towards the task of obtaining reservation confirmation")
  first_name: Optional[str] = Field(default=None, description="The first name of user completing the task, if any")
  last_name: Optional[str] = Field(default=None, description="The last name of user completing the task, if any")
  party_size: Optional[int] = Field(default=None, description="Party size of reservation, if any")
  datetime: Optional[Datetime] = Field(default=None, description="Date time of the reservation in a isoformat YYYY-MM-DDTHH:MM:SS, if any")
  date: Optional[Date] = Field(default=None, description="Date of the reservation compatible with Python's datetime.fromisoformat() method")
  time: Optional[Time] = Field(default=None, description="Time of the reservation compatible with Python's datetime.fromisoformat() method")
  restaurant_name: Optional[str] = Field(default=None, description="Name of restaurant, if any")
  is_first_name_correct: Optional[str] = Field(default=None, description="The first name of user completing the task, if available")
  # boolean metrics
  is_name_correct: Optional[bool] = Field(default=None, description="whether the first and last name of reservation match between the user query and the screenshot or html webpage, if available")
  is_party_size_correct: Optional[bool] = Field(default=None, description="whether the party size of the reservation match between the user query and the webpage, if available for comparison")
  is_datetime_correct: Optional[bool] = Field(default=None, description="whether the date & time of reservation match between the user query and the webpage, if available for comparison")
  is_restaurant_name_correct: Optional[bool] = Field(default=None, description="whether the restaurant name of reservation match between the webpage, if available for comparison")
  accuracy: Optional[float] = Field(..., description="the accuracy score between 0-1 on the fields of interest between the user query and the webpage. If the user did not specifiy, do not account for it in the score. For this case the fields of interest are: first_name, last_name, party_size, date, time, restaurant_name. ")
  
  

@dataclass
class opentable_html_input:
    """
    Dataclass for specifying the structure of the input DataFrame expected by
    the opentable_reservation_html metric class.
    
    Attributes:
        DOM (pd.Series[str]): A series containing HTML content as strings.
        restaurant_name (Optional[pd.Series[str]]): Optional series containing restaurant names.
        status (Optional[pd.Series[str]]): Optional series containing reservation statuses.
        num_people (Optional[pd.Series[int]]): Optional series containing the number of people per reservation.
        date_time (Optional[pd.Series[str]]): Optional series containing date and time of reservations.
        first_name (Optional[pd.Series[str]]): Optional series containing first names.
        last_name (Optional[pd.Series[str]]): Optional series containing last names.
    """
    DOM: pd.Series
    restaurant_name: Optional[pd.Series] = None
    status: Optional[pd.Series] = None
    num_people: Optional[pd.Series] = None
    date_time: Optional[pd.Series] = None
    first_name: Optional[pd.Series] = None
    last_name: Optional[pd.Series] = None