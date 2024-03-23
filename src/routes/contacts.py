import pathlib
from datetime import date, timedelta
from fastapi import APIRouter, HTTPException, Depends, status, Query, Path, UploadFile, File
from sqlalchemy.orm import Session
from typing import List

from src.database.db import get_db
from src.database.models import Contact
from src.repository import contacts as repository_contacts
from src.schemas import ContactModel, ContactResponse

router = APIRouter(prefix='/contacts')

"""
Отримати список всіх контактів.
Валідація не відбувається.
"""


@router.get("/", response_model=List[ContactResponse], tags=['Contacts'])
async def get_contacts(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    contacts = await repository_contacts.get_contacts(skip, limit, db)
    return contacts


"""
Отримати один контакт за ідентифікатором.
Валідація:
1) Чи існує контакт в базі даних?
"""


@router.get("/{contact_id}", response_model=ContactResponse, tags=['Contacts'])
async def get_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await repository_contacts.get_contact(contact_id, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


"""
Створити новий контакт.
Валідація:
1) Чи відповідає номер формату? (schemas.py)
2) Чи день народження в майбутньому? (schemas.py)
3) Чи існує контакт з надісланою електронною поштою?
4) Чи існує контакт з надісланим номером телефону?
"""


@router.post("/", response_model=ContactResponse, tags=['Contacts'])
async def create_contact(body: ContactModel, db: Session = Depends(get_db)):
    contact_email = db.query(Contact).filter_by(email=body.email).first()
    contact_number = db.query(Contact).filter_by(contact_number=body.contact_number).first()

    if contact_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with the mentioned email already exists."
        )

    if contact_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with the mentioned contact number already exists."
        )

    return await repository_contacts.create_contact(body, db)


"""
Оновити існуючий контакт.
Валідація:
1) Чи відповідає номер формату? (schemas.py)
1) Чи день народження в майбутньому? (schemas.py)
2) Чи відповідає електронна адреса формату? (schemas.py)
3) Чи існує контакт в базі даних?
4) Чи існує контакт з надісланою електронною поштою?
5) Чи існує контакт з надісланим номером телефону?

"""


@router.put("/{contact_id}", response_model=ContactResponse, tags=['Contacts'])
async def update_contact(body: ContactModel, contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()

    if contact is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")

    contact_email = db.query(Contact).filter_by(email=body.email).first()
    contact_number = db.query(Contact).filter_by(contact_number=body.contact_number).first()

    if contact_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with the mentioned email already exists."
        )

    if contact_number:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Contact with the mentioned contact number already exists."
        )

    contact = await repository_contacts.update_contact(contact_id, body, db)

    return contact


"""
Видалити контакт.
Валідація:
1) Чи існує контакт в базі даних?
"""


@router.delete("/{contact_id}", response_model=ContactResponse, tags=['Contacts'])
async def remove_contact(contact_id: int = Path(ge=1), db: Session = Depends(get_db)):
    contact = await repository_contacts.remove_contact(contact_id, db)
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found"
        )
    return contact


"""
Контакти повинні бути доступні для пошуку за іменем, прізвищем чи адресою електронної пошти (Query).
Валідація:
1) Чи існує контакт з вказаним параметром(ім'ям, прізвищем або електронною адресою) в базі даних? (repository func)
"""


@router.put("/search/{contact_id}", response_model=List[ContactResponse], tags=['Contacts'])
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
API повинен мати змогу отримати список контактів з днями народження на найближчі 7 днів.
Валідація не відбувається.
"""


@router.get("/birthdays/", response_model=List[ContactResponse], tags=['Birthdays'])
async def get_upcoming_birthdays(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    current_date = date.today()
    to_date = current_date + timedelta(days=7)

    birthdays = await repository_contacts.upcoming_birthdays(current_date, to_date, skip, limit, db)
    return birthdays


"""
Завантаження файлу.
"""

MAX_FILE_SIZE = 1_000_000


@router.post("/upload-file/", tags=['Upload File'])
async def upload_file(file: UploadFile = File()):
    pathlib.Path("uploads").mkdir(exist_ok=True)
    file_path = f"uploads/{file.filename}"

    file_size = 0
    with open(file_path, "wb") as f:
        while True:
            chunk = await file.read(1024)
            if not chunk:
                break
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                f.close()
                pathlib.Path(file_path).unlink()
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large, max size is {MAX_FILE_SIZE} bytes"
                )
            f.write(chunk)
    return {"file_path": file_path}
