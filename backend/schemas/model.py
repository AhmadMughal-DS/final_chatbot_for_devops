import pydantic_core
from pydantic_core import SchemaValidator
from typing import Any, Dict, List, Optional, Tuple, Type, Union
from pydantic_core import core_schema
from pydantic import BaseModel, EmailStr

class SignupModel(BaseModel):
    email: EmailStr
    password: str
