from model.firestore_model import FirestoreModel


class User(FirestoreModel):

    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.email: str = ''
        self.bytes: bytes = bytes()


User.set_collection('users')


def create_user():
    user_dict = {'name': 'Nayan', 'email': 'nayan@crazyideas.co.in', 'bytes': bytes([0xC1, 0xC2, 0x01])}
    user: User = User.create_from_dict(user_dict)
    print(user.doc_id, user.bytes)


def read_user():
    user = User.query.get_by_id('PKXRIZUvTU5iCOoI3XXf')
    print(user.name, user.bytes)


if __name__ == '__main__':
    read_user()
