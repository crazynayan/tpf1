import os
from base64 import b64encode

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "google-cloud-tokyo.json"

from p7_flask_app.auth import User


def create_user(email: str):
    if not isinstance(email, str) or sum(1 for char in email if char == "@") != 1:
        print(f"Invalid email - {email}")
        return
    if User.objects.filter_by(email=email).first():
        print(f"Email already exists")
        return
    user = User()
    user.email = email
    password = b64encode(os.urandom(24)).decode()
    user.set_password(password)
    user.set_id(email.replace("@", "_").replace(".", "-"))
    user.save()
    print(f"User {email} created. Your password is {password}")
    return
