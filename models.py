from pydantic import BaseModel
from typing import Dict, Optional
from enum import Enum


class DropdownChoice(str, Enum):
    choice1 = 'Choice 1'
    choice2 = 'Choice 2'
    choice3 = 'Choice 3'


class PDFData(BaseModel):
    name: str
    dropdownChoice: DropdownChoice
    checkbox1: Optional[bool]
    checkbox2: Optional[bool]
    checkbox3: Optional[bool]
    nameOfDependant: str
    ageOfDependant: str

    def to_form_schema_dict(self) -> Dict[str, Optional[str]]:
        """Convert PDFData to a dictionary with the required schema."""
        return {
            'Age\t of Dependent': self.ageOfDependant,
            'Dropdown2': self.dropdownChoice,
            'Name': self.name,
            'Name of Dependent': self.nameOfDependant,
            'Option 1': bool(self.checkbox1),
            'Option 2': bool(self.checkbox2),
            'Option 3': bool(self.checkbox3),
        }
