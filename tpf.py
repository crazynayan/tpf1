import os
from base64 import b64encode

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud-tokyo.json"

from p7_flask_app.auth import User


def create_user(email: str, initial: str):
    if not isinstance(email, str) or sum(1 for char in email if char == "@") != 1 or "|" in email:
        print(f"Invalid email - {email}")
        return
    if User.objects.filter_by(email=email).first():
        print(f"Email already exists")
        return
    if not isinstance(initial, str) or len(initial) != 2 or not initial.isalpha():
        print(f"Initial should be 2 character alphabet string")
        return
    if User.objects.filter_by(initial=initial).first():
        print(f"Initial already exits")
        return
    user = User()
    user.email = email
    user.initial = initial.upper()
    password = b64encode(os.urandom(24)).decode()
    user.set_password(password)
    user.set_id(email.replace("@", "_").replace(".", "-"))
    user.save()
    print(f"User {user.email} created with initial {user.initial}. Your password is {password}")
    return
