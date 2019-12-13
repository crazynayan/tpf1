from typing import List
from unittest import TestCase

from firestore.firestore_ci import FirestoreDocument, ORDER_DESCENDING, FirestoreCIError


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
        self.amount_pending: int = 0
        self.contacts: List[str] = list()


User.init()
Client.init()


class FirestoreTest(TestCase):
    def setUp(self) -> None:
        self.nayan_dict = {
            'name': 'Nayan',
            'email': 'nayan@crazyideas.co.in',
            'clients': [
                {
                    'name': 'Nayan',
                    'address': 'Mumbai',
                    'account_type': 'Individual',
                    'amount_pending': 5000,
                    'contacts': ['+91 91234 50001', '+91 91234 50002'],
                },
            ]
        }
        self.avani_dict = {
            'name': 'Avani',
            'email': 'avani@crazyideas.co.in',
            'clients': [
                {
                    'name': 'Avani',
                    'address': 'Netherlands',
                    'account_type': 'Individual',
                    'amount_pending': 1100,
                    'contacts': ['+31 612 345 001'],
                },
                {
                    'name': 'Hiten',
                    'address': 'Netherlands',
                    'account_type': 'Individual',
                    'amount_pending': 0,
                    'contacts': [],
                },
                {
                    'name': 'Crazy Ideas',
                    'address': 'Mumbai',
                    'account_type': 'Partnership Firm',
                    'amount_pending': 0,
                    'contacts': ['+91 91234 50011', '+91 91234 50012', '+91 91234 50013'],
                },
            ]
        }
        User.objects.cascade.filter_by(name='Nayan').delete()
        User.objects.cascade.filter_by(name='Avani').delete()
        self.nayan: User = User.create_from_dict(self.nayan_dict)
        self.avani: User = User.create_from_dict(self.avani_dict)
        self.nayan_dict['id'] = self.nayan.id
        self.nayan_dict['clients'][0]['id'] = self.nayan.clients[0].id
        self.avani_dict['id'] = self.avani.id
        self.avani_dict['clients'][0]['id'] = self.avani.clients[0].id
        self.avani_dict['clients'][1]['id'] = self.avani.clients[1].id
        self.avani_dict['clients'][2]['id'] = self.avani.clients[2].id

    def test_create(self):
        # Nayan - Client #1
        self.assertEqual(f"/users/{self.nayan.id}", str(self.nayan))
        self.assertEqual('nayan@crazyideas.co.in', self.nayan.email)
        self.assertEqual('/clients/None', str(self.nayan.clients[0]))
        self.assertEqual('Nayan', self.nayan.clients[0].name)
        self.assertEqual('Mumbai', self.nayan.clients[0].address)
        # Avani - Client #1
        self.assertEqual(f"/users/{self.avani.id}", str(self.avani))
        self.assertEqual('avani@crazyideas.co.in', self.avani.email)
        self.assertEqual('/clients/None', str(self.avani.clients[0]))
        self.assertEqual('Avani', self.avani.clients[0].name)
        self.assertEqual('Netherlands', self.avani.clients[0].address)
        # Avani - Client #2
        self.assertEqual('/clients/None', str(self.avani.clients[1]))
        self.assertEqual('Hiten', self.avani.clients[1].name)
        self.assertEqual('Netherlands', self.avani.clients[1].address)
        self.assertEqual('Individual', self.avani.clients[1].account_type)
        # Avani - Client #3
        self.assertEqual('/clients/None', str(self.avani.clients[2]))
        self.assertEqual('Crazy Ideas', self.avani.clients[2].name)
        self.assertEqual('Mumbai', self.avani.clients[2].address)
        self.assertEqual('Partnership Firm', self.avani.clients[2].account_type)

    def test_read(self):
        # Set ID in dict for later comparison with cascade_to_dict
        nayan: User = User.objects.cascade.filter_by(name='Nayan').first()
        avani: User = User.objects.cascade.filter_by(name='Avani').first()
        self.nayan_dict['id'] = nayan.id
        self.nayan_dict['clients'][0]['id'] = nayan.clients[0].id
        self.avani_dict['id'] = avani.id
        self.avani_dict['clients'][0]['id'] = avani.clients[0].id
        self.avani_dict['clients'][1]['id'] = avani.clients[1].id
        self.avani_dict['clients'][2]['id'] = avani.clients[2].id
        # Test filter_by and first
        nayan: User = User.objects.filter_by(name='Nayan').first()
        self.assertEqual(f"/users/{nayan.id}", str(nayan))
        self.assertEqual('Nayan', nayan.name)
        nayan_client: Client = Client.objects.filter_by(name='Nayan').first()
        self.assertListEqual([nayan_client.id], nayan.clients)
        # Test cascade_to_dict
        self.assertEqual(self.avani_dict, User.objects.cascade.filter_by(name='Avani').first().cascade_to_dict())
        self.assertEqual(self.nayan_dict, User.objects.cascade.filter_by(name='Nayan').first().cascade_to_dict())
        # Test filter, cascade and get
        avani: List[User] = User.objects.cascade.filter('email', '==', 'avani@crazyideas.co.in').get()
        avani: User = next(iter(avani))  # or avani: User = avani[0]
        self.assertEqual(f"/users/{avani.id}", str(avani))
        self.assertEqual('Avani', avani.name)
        self.assertListEqual(['Avani', 'Hiten', 'Crazy Ideas'], [client.name for client in avani.clients])
        # Test order_by and limit
        clients: List[Client] = Client.objects.order_by('name', ORDER_DESCENDING).limit(100).get()
        self.assertListEqual(['Nayan', 'Hiten', 'Crazy Ideas', 'Avani'], [client.name for client in clients])
        clients: List[Client] = Client.objects.order_by('name').limit(3).get()
        self.assertListEqual(['Avani', 'Crazy Ideas', 'Hiten'], [client.name for client in clients])
        client: Client = Client.objects.order_by('name').first()
        self.assertEqual('Avani', client.name)
        client: Client = Client.objects.limit(0).first()  # limit does not work with first; first overrides the limit
        self.assertIsNotNone(client.name)
        clients: List[Client] = Client.objects.limit(0).get()  # limit of 0 or negative returns an empty list with get
        self.assertListEqual(list(), clients)
        clients: List[Client] = Client.objects.limit(-3).get()
        self.assertListEqual(list(), clients)
        self.assertIsNone(User.get_by_id('invalid id'))
        # Test exceptions
        self.assertRaises(FirestoreCIError, User.objects.filter, 'invalid', '==', 'some data')
        self.assertRaises(FirestoreCIError, User.objects.filter, 'email', '!=', 'some data')
        self.assertRaises(FirestoreCIError, User.objects.filter_by, invalid='some data')
        self.assertRaises(FirestoreCIError, User.objects.order_by, 'invalid')
        self.assertRaises(FirestoreCIError, User.objects.order_by, 'email', 'desc')

    def test_update(self):
        # Test on objects returned by create (Works only on objects that do not have child objects)
        self.nayan.name = 'Nayan Zaveri'
        self.assertEqual(False, self.nayan.save())  # Will not save on the parent object
        self.assertEqual('Nayan', User.get_by_id(self.nayan.id).name)
        self.nayan.clients[0].name = 'Nayan Zaveri'
        self.assertEqual(False, self.nayan.save(cascade=True))  # Will not save on the child object
        self.assertIsNone(Client.objects.filter_by(name='Nayan Zaveri').first())
        new_client = Client.create_from_dict({'name': 'Nayan HUF', 'address': 'India', 'account_type': 'HUF'})
        self.assertEqual('India', new_client.address)
        new_client.address = 'Mumbai'
        self.assertEqual(True, new_client.save())  # Will save since it does not contain any child objects
        self.assertEqual('Mumbai', Client.objects.filter_by(name='Nayan HUF').first().address)
        # Better to retrieve the objects and save
        nayan: User = User.objects.cascade.filter_by(name='Nayan').first()
        nayan.name = 'Nayan Zaveri'
        self.assertEqual(True, nayan.save())  # Will save on the parent object
        self.assertEqual('Nayan Zaveri', User.get_by_id(nayan.id).name)
        nayan.name = 'Nayan'
        nayan.clients[0].address = 'Dallas/Fort Worth'
        self.assertEqual(True, nayan.save(cascade=True))  # Will now save on the child object also
        self.assertEqual('Dallas/Fort Worth', Client.objects.filter_by(name='Nayan').first().address)
        self.assertEqual('Nayan', User.get_by_id(nayan.id).name)
        # Link a child object manually without using cascade
        nayan: User = User.objects.filter_by(name='Nayan').first()  # Don't use cascade here
        nayan.clients.append(new_client.id)
        self.assertEqual(True, nayan.save())  # cascade=True not required here since nayan does not contain Client
        nayan: User = User.objects.cascade.filter_by(name='Nayan').first()  # Use cascade to test nested clients
        self.assertEqual(2, len(nayan.clients))
        self.assertEqual('Nayan HUF', nayan.clients[1].name)

    def test_delete(self) -> None:
        # Test delete on created objects
        self.assertEqual(str(), self.nayan.delete())  # Will not delete since it contains child reference as None
        self.assertEqual(str(), self.nayan.delete(cascade=True))
        self.assertEqual('Nayan', User.get_by_id(self.nayan.id).name)
        # Test direct delete of object with no child
        deleted_id = Client.objects.filter_by(name='Nayan').delete()
        self.assertNotEqual(str(), deleted_id)  # Will delete
        self.assertIsNone(Client.objects.filter_by(name='Nayan').first())
        # But it leaves a dangling reference in the database
        nayan = User.objects.filter_by(name='Nayan').first()  # Not use cascade so ids are retrieved
        self.assertEqual(1, len(nayan.clients))
        self.assertEqual(deleted_id, nayan.clients[0])
        nayan_whole = User.objects.cascade.filter_by(name='Nayan').first()
        self.assertEqual(1, len(nayan_whole.clients))
        self.assertIsNone(nayan_whole.clients[0])
        # Fix it by removing the dangling reference
        nayan.clients.remove(deleted_id)
        nayan.save()
        self.assertEqual(0, len(nayan.clients))
        nayan_whole = User.objects.cascade.filter_by(name='Nayan').first()
        self.assertEqual(0, len(nayan_whole.clients))
        # Deleting a child object without using id (Not applicable for many-to-many relationship)
        # 1 Read the parent object with cascade (Needs to be done before Step #2)
        # 2 Delete the child document
        # 3 Remove the child object from the parent object.
        # 4 Save the parent object
        avani = User.objects.cascade.filter_by(name='Avani').first()
        Client.objects.filter_by(name='Crazy Ideas').delete()
        avani.clients.remove(next(client for client in avani.clients if client.name == 'Crazy Ideas'))
        avani.save()
        self.assertEqual(2, len(User.objects.filter_by(name='Avani').first().clients))
        # Delete a child object using id
        # 1 Read the parent object without cascade
        # 2 Delete the child document and get its id
        # 3 Remove the deleted id from the parent object
        # 4 Save the parent object
        avani = User.objects.filter_by(name='Avani').first()  # Read without cascade
        deleted_id = Client.objects.filter_by(name='Hiten').delete()
        avani.clients.remove(deleted_id)
        avani.save()
        self.assertEqual(1, len(User.objects.filter_by(name='Avani').first().clients))

    def tearDown(self) -> None:
        User.objects.cascade.filter_by(name='Nayan').delete()
        User.objects.cascade.filter_by(name='Avani').delete()
