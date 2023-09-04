# import route dependencies instead of creating an app
from fastapi import APIRouter, Depends
from firebase_admin import auth
from google.oauth2.id_token import verify_firebase_token

from src.AdminFastAPIBackend.BaseClasses.UsersBaseClasses import InputAppUser, OuputAppUser
from src.logger import setup_logger

router = APIRouter()
logger = setup_logger(__name__)


@router.post("/create_user/")
async def create_new_user(user: InputAppUser, decoded_token: dict = Depends(verify_firebase_token)):
    """Create a new user in Firebase Auth and Firestore
    incoming user object does not need uid prepopulated (will be generated by firebase)
    """

    print(f'{decoded_token = }')

    try:

        assert user.email or user.phone_number, "Must provide either email or phone number"

        user = auth.create_user(
            email=user.email,
            password=user.password,
            display_name=user.display_name,
            phone_number=user.phone_number,  # make sure is properly formatted ... document this
            photo_url=user.photo_url,
            email_verified=False
        )

        # Cr

        # add to firestore
        print('Sucessfully created new user: {0}'.format(user.uid))
        user = OuputAppUser(
            uid=user.uid,
            email=user.email,
            display_name=user.display_name,
            phone_number=user.phone_number,
            photo_url=user.photo_url,
            email_verified=user.email_verified
        )
        return user
    except Exception as e:
        print('Error creating new user: {0}'.format(e))


@router.delete("/delete_user/")
async def delete_user(user: InputAppUser):
    try:
        assert user.uid, "Must provide a uid"

        user = auth.delete_user(user.uid)
        # add to firestore
        print('Sucessfully deleted user: {0}'.format(user.uid))

    except Exception as e:
        print('Error deleting user: {0}'.format(e))


@router.get("/get_user/")
async def get_user(user: InputAppUser):
    try:
        assert user.uid, "Must provide a uid"

        user = auth.get_user(user.uid)
        # add to firestore
        print('Sucessfully retrieved user: {0}'.format(user.uid))
        user = OuputAppUser(**user.__dict__)

        return user

    except Exception as e:
        print('Error retrieving user: {0}'.format(e))


@router.get("/get_user_by_email/")
async def get_user_by_email(user: InputAppUser):
    try:
        assert user.email, "Must provide a email"

        user = auth.get_user_by_email(user.email)
        # add to firestore
        print('Sucessfully retrieved user: {0}'.format(user.email))
        user = OuputAppUser(**user.__dict__)

        return user

    except Exception as e:
        print('Error retrieving user: {0}'.format(e))


@router.get("/get_user_by_phone/")
async def get_user_by_phone(user: InputAppUser):
    try:
        assert user.phone_number, "Must provide a phone_number"

        user = auth.get_user_by_phone_number(user.phone_number)
        # add to firestore
        print('Sucessfully retrieved user: {0}'.format(user.phone_number))
        user = OuputAppUser(**user.__dict__)

        return user
    except Exception as e:
        print('Error retrieving user: {0}'.format(e))


@router.get("/get_all_users/")
async def get_all_users():
    try:
        users = auth.list_users()
        # add to firestore
        print('Sucessfully retrieved all users')

        print(users.users[0])
        print(users.users[0].__dict__)
        print(OuputAppUser(**users.users[0].__dict__).__dict__)

        users = [OuputAppUser(**user.__dict__) for user in users.users]

        return users
    except Exception as e:
        print('Error retrieving all users: {0}'.format(e))