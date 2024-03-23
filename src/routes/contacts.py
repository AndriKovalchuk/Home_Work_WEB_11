from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Query
from typing import List
from sqlalchemy.orm import Session

from src.database.db import get_db
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel, ContactResponse

router = APIRouter(prefix='/contacts', tags=['contacts'])

"""
Отримати список всіх контактів
"""


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


"""
Отримати один контакт за ідентифікатором
"""


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


"""
Створити новий контакт
"""


@router.post("/", response_model=ContactResponse)
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    return await repository_contacts.create_contact(body, db)


"""
Оновити існуючий контакт
"""


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(contact_id: int, body: ContactModel, db: Session = Depends(get_db)):
    contact = await repository_contacts.update_contact(contact_id, body, db)
    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    return contact


"""
Видалити контакт
"""


@router.delete("/{contact_id}", response_model=ContactResponse)
async def remove_contact(contact_id: int, db: Session = Depends(get_db)):
    return await repository_contacts.remove_contact(contact_id, db)


"""
Контакти повинні бути доступні для пошуку за іменем, прізвищем чи адресою електронної пошти (Query)
"""


@router.put("/search/{contact_id}", response_model=List[ContactResponse])
async def find_contact(contact_first_name: str = Query(None),
                       contact_last_name: str = Query(None),
                       contact_email: str = Query(None),
                       db: Session = Depends(get_db)):
    if contact_first_name:
        return await repository_contacts.find_contact_by_first_name(contact_first_name, db)
    elif contact_last_name:
        return await repository_contacts.find_contact_by_last_name(contact_last_name, db)
    elif contact_email:
        return await repository_contacts.find_contact_by_email(contact_email, db)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You must provide at least one parameter"
        )


"""
API повинен мати змогу отримати список контактів з днями народження на найближчі 7 днів
"""


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    current_date = date.today()
    to_date = current_date + timedelta(days=7)

    birthdays = await repository_contacts.upcoming_birthdays(current_date, to_date, skip, limit, db)
    return birthdays
