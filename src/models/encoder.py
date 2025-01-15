import json
from sqlalchemy.types import TypeDecorator, JSON
from pydantic import ValidationError
from models.details import Recipe

class JSONEncodedRecipe(TypeDecorator):
    impl = JSON

    def process_bind_param(self, value, dialect):
        """Serialize the Recipe object to JSON."""
        if value is not None:
            if isinstance(value, Recipe):
                return value.model_dump()  # Convert Pydantic model to a dictionary
            raise ValueError("Expected a Recipe object for the 'data' field")
        return value

    def process_result_value(self, value, dialect):
        """Deserialize JSON to a Recipe object."""
        if value is not None:
            try:
                return Recipe.model_validate(value)
            except ValidationError as e:
                raise ValueError(f"Invalid data for Recipe model: {e}")
        return value
