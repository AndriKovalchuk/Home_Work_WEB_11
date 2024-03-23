from fastapi import HTTPException
from starlette import status
from sqlalchemy.orm import Session
from typing import List

from src.schemas import ContactModel
from src.database.models import Contact


async def get_contacts(skip: int, limit: int, db: Session) -> List[Contact]:
    return db.query(Contact).offset(skip).limit(limit).all()  # noqa


async def get_contact(contact_id: int, db: Session) -> Contact:
    return db.query(Contact).filter(Contact.id == contact_id).first()  # noqa


async def create_contact(body: ContactModel, db: Session) -> Contact:
    contact = Contact(first_name=body.first_name,
                      last_name=body.last_name,
                      email=body.email,
                      contact_number=body.contact_number,
                      birth_date=body.birth_date,
                      additional_information=body.additional_information
                      )
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


async def update_contact(contact_id: int, body: ContactModel, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        contact.first_name = body.first_name
        contact.last_name = body.last_name
        contact.email = body.email
        contact.contact_number = body.contact_number
        contact.birth_date = body.birth_date
        contact.additional_information = body.additional_information
        db.commit()
    return contact


async def remove_contact(contact_id: int, db: Session) -> Contact | None:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact:
        db.delete(contact)
        db.commit()
    return contact


async def find_contact_by_first_name(contact_first_name: str, db: Session) -> List[Contact]:
    """
    Пошук контакту за іменем.
    """
    contact = db.query(Contact).filter(Contact.first_name == contact_first_name).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact  # noqa


async def find_contact_by_last_name(contact_last_name: str, db: Session) -> List[Contact]:
    """
    Пошук контакту за прізвищем.
    """
    contact = db.query(Contact).filter(Contact.last_name == contact_last_name).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact  # noqa


async def find_contact_by_email(contact_email: str, db: Session) -> List[Contact]:
    """
        Пошук контакту за адресою електронної пошти.
    """
    contact = db.query(Contact).filter(Contact.email == contact_email).all()
    if not contact:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    else:
        return contact  # noqa


"""
API повинен мати змогу отримати список контактів з днями народження на найближчі 7 днів.
"""


async def upcoming_birthdays(current_date, to_date, skip: int, limit: int, db: Session) -> List[Contact]:
    contacts = db.query(Contact).offset(skip).limit(limit).all()

    upcoming = []

    for contact in contacts:

        contact_birthday_month_day = (contact.birth_date.month, contact.birth_date.day)
        current_date_month_day = (current_date.month, current_date.day)
        to_date_month_day = (to_date.month, to_date.day)

        if current_date_month_day < contact_birthday_month_day <= to_date_month_day:
            upcoming.append(contact)

    return upcoming  # noqa
