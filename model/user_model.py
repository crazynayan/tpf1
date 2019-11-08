from typing import List

from model.firestore_ci import FirestoreDocument, ORDER_DESCENDING


class User(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.email: str = ''
        self.clients: List[Client] = list()


class Client(FirestoreDocument):

    def __init__(self):
        super().__init__()
        self.name: str = ''
        self.address: str = ''
        self.account_type: str = ''


User.init(collection='users')
Client.init()


def create_user():
    nayan_dict = {
        'name': 'Nayan',
        'email': 'nayan@crazyideas.co.in',
        'clients': {
            'name': 'Nayan',
            'address': 'Mumbai',
            'account_type': 'Individual',
        },
    }
    avani_dict = {
        'name': 'Avani',
        'email': 'avani@crazyideas.co.in',
        'clients': [
            {
                'name': 'Avani',
                'address': 'Netherlands',
                'account_type': 'Individual',
            },
            {
                'name': 'Hiten',
                'address': 'Netherlands',
                'account_type': 'Individual',
            },
            {
                'name': 'Crazy Ideas',
                'address': 'Mumbai',
                'account_type': 'Partnership Firm'
            },
        ]

    }
    nayan: User = User.create_from_dict(nayan_dict)
    avani: User = User.create_from_dict(avani_dict)
    print(nayan, nayan.email)
    for client in nayan.clients:
        print('\t', client, client.name, client.address)
    print(avani, avani.email)
    for client in avani.clients:
        print('\t', client, client.name, client.address)
    return


def read_user():
    # users = User.objects.cascade.get()
    # for user in users:
    #     print(user, user.email)
    #     for client in user.clients:
    #         print('\t', client, client.name, client.address)
    # nayan = User.objects.filter_by(name='Nayan').first()
    # print(nayan, nayan.name, nayan.clients)
    # avani = User.objects.filter('email', '==', 'avani@crazyideas.co.in').cascade.get()[0]
    # print(avani, avani.name, [client.name for client in avani.clients])
    clients = Client.objects.order_by('name', ORDER_DESCENDING).limit(100).get()
    print([client.name for client in clients])
    client = Client.objects.limit(3).first()
    print(client.name)
    return


if __name__ == '__main__':
    read_user()
