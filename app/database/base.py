from sqlalchemy.orm import declarative_base

Base = declarative_base()

from app.models.preference import Preference # noqa