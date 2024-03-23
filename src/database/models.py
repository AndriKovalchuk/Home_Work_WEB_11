from sqlalchemy import Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    first_name = Column(String(15), nullable=False)
    last_name = Column(String(15), nullable=False)
    email = Column(String, nullable=False, unique=True)
    contact_number = Column(String(20), nullable=False, unique=True)
    birth_date = Column(Date, nullable=False)
    additional_information = Column(String(250))
