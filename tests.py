import base64
import datetime
import json

from django.test import TestCase, Client
from django.test import RequestFactory

# Create your tests here.

from core.models import User, WorkPlace, Reservation
from core.utils import get_reservation, get_date


class ModelsPlaceTestCase(TestCase):
    date_time_now = datetime.datetime.now()

    def setUp(self):
        workplace = WorkPlace.objects.create(name="work", address="address")
        user = User.objects.create_user(username="username2", email="email@email.email", password="Qwerty123")
        admin = User.objects.create_user(username="admin", email="admin@email.email", password="admin", is_staff=True,
                                         is_superuser=True)

        Reservation.objects.create(user=user, workplace=workplace,
                                   date_from=self.date_time_now + datetime.timedelta(hours=4),
                                   date_to=self.date_time_now + datetime.timedelta(hours=8))
        self.factory = RequestFactory()
        self.client = Client()

    def test_get_reservation(self):
        test_reservation = list(Reservation.objects.filter(id=1))
        self.assertEqual(test_reservation, list(
            get_reservation(self.date_time_now + datetime.timedelta(hours=5),
                            self.date_time_now + datetime.timedelta(hours=9))))
        self.assertEqual(test_reservation, list(
            get_reservation(self.date_time_now + datetime.timedelta(hours=5),
                            self.date_time_now + datetime.timedelta(hours=7))))
        self.assertEqual(test_reservation, list(
            get_reservation(self.date_time_now + datetime.timedelta(hours=5),
                            self.date_time_now + datetime.timedelta(hours=7))))
        self.assertEqual(test_reservation, list(
            get_reservation(self.date_time_now + datetime.timedelta(hours=4),
                            self.date_time_now + datetime.timedelta(hours=8))))
        self.assertEqual(test_reservation, list(
            get_reservation(self.date_time_now + datetime.timedelta(hours=4, minutes=30),
                            self.date_time_now + datetime.timedelta(hours=7))))
        self.assertFalse(
            get_reservation(self.date_time_now + datetime.timedelta(hours=2),
                            self.date_time_now + datetime.timedelta(hours=3)).exists())
        self.assertFalse(
            get_reservation(self.date_time_now + datetime.timedelta(hours=9),
                            self.date_time_now + datetime.timedelta(hours=9, minutes=30)).exists())

    def test_get_date(self):
        request = self.factory.get('/')
        real_datetime_from = self.date_time_now + datetime.timedelta(hours=4, minutes=30)
        datetime_from = str(real_datetime_from)
        real_datetime_to = self.date_time_now + datetime.timedelta(hours=5)
        datetime_to = str(real_datetime_to)
        request.data = {'datetime_from': datetime_from, 'datetime_to': datetime_to}
        self.assertEqual((real_datetime_from, real_datetime_to), (get_date(request)),
                         'datetime_from and datetime_to are included')
        request.data = {'datetime_from': datetime_from}
        new_datetime_from, new_datetime_to = get_date(request)
        datetime_from_get_date = real_datetime_from + datetime.timedelta(hours=8)
        self.assertEqual(real_datetime_from, new_datetime_from, 'only is included')
        datetime_to_get_date = real_datetime_from + datetime.timedelta(hours=8)
        self.assertTrue(datetime_from_get_date <= new_datetime_to <= datetime_to_get_date, 'only is included')
        request.data = {'datetime_from': 'datetime_from'}
        with self.assertRaises(Exception) as context:
            get_date(request)
        self.assertTrue('Unknown string format: datetime_from' in str(context.exception))
        request.data = {'datetime_from': 'datetime_from'}
        with self.assertRaises(Exception) as context:
            get_date(request)
        self.assertTrue('Unknown string format: datetime_from' in str(context.exception),
                        'Unknown string format: datetime_from')
        request.data = {'datetime_to': 'datetime_to'}
        with self.assertRaises(Exception) as context:
            get_date(request)
        self.assertTrue('Unknown string format: datetime_to' in str(context.exception),
                        'Unknown string format: datetime_to')
        request.data = {'datetime_from': datetime_to, 'datetime_to': datetime_from}
        with self.assertRaises(ValueError) as context:
            get_date(request)
        self.assertTrue('datetime_from < datetime_to' in str(context.exception), 'datetime_from < datetime_to')

        request.data = {'datetime_from': str(self.date_time_now - datetime.timedelta(hours=4)),
                                'datetime_to': datetime_from}
        with self.assertRaises(ValueError) as context:
            get_date(request)
        self.assertTrue('datetime_from < date_time_now' in str(context.exception), 'datetime_from < date_time_now')

    def test_register(self):
        response = self.client.post('/api/register/', {'first name': 'UserName', 'password': 'smith'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(str('{"Username": "UserName"}') in str(response.content))
        self.assertEqual(User.objects.get(username="UserName").first_name, 'UserName')
        response = self.client.post('/api/register/', {'password': 'smith'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue('add first_name or last_name' in str(response.content))
        response = self.client.post('/api/register/',
                                    {'first name': 'UserName1', 'email': 'email', 'password': 'smith'})
        self.assertEqual(response.status_code, 400)
        self.assertTrue('Not valid email' in str(response.content))

    def test_vacant_space(self):
        workplace2 = WorkPlace.objects.create(name="work2", address="address2")
        workplace2_result = {"Answer": [{'id': 2, 'name': 'work2', 'address': 'address2'}]}
        all_workplace = {"Answer": [{"id": 1, "name": "work", "address": "address"},
                         {"id": 2, "name": "work2", "address": "address2"}]}
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'admin:admin').decode("ascii"),
        }
        response = self.client.get(
            '/api/vacant_space/?datetime_from=' + str(self.date_time_now + datetime.timedelta(hours=4)),
            **auth_headers)
        self.assertEquals(response.status_code, 200, 'status_code = 200')
        self.assertEquals(workplace2_result, json.loads(response.content), 'HTTP_AUTHORIZATION + datetime_from')
        response = self.client.get('/api/vacant_space/', **auth_headers)
        self.assertEquals(workplace2_result, json.loads(response.content), 'only HTTP_AUTHORIZATION')
        self.assertEquals(response.status_code, 200, 'status_code = 200')
        response = self.client.get('/api/vacant_space/?datetime_from=' + str(
            self.date_time_now + datetime.timedelta(hours=1)) + '&datetime_to='
                                   + str(self.date_time_now + datetime.timedelta(hours=2)), **auth_headers)

        self.assertEquals(all_workplace, json.loads(response.content), 'all workplace')
        self.assertEquals(response.status_code, 200, 'status_code = 200')

        response = self.client.get('/api/vacant_space/?datetime_from=datetime_from',
                                   **auth_headers)
        self.assertTrue('Please, use right date format: Unknown string format: datetime_from' in str(response.content),
                        'use right date format')
        self.assertEquals(response.status_code, 400, 'status_code = 400')
        response = self.client.get(
            '/api/vacant_space/?datetime_from=' + str(self.date_time_now - datetime.timedelta(minutes=1)),
            **auth_headers)
        self.assertTrue('Please, use right date format: datetime_from < date_time_now' in str(response.content),
                        'datetime_from < date_time_now')
        self.assertEquals(response.status_code, 400, 'status_code = 400')
        response = self.client.get(
            '/api/vacant_space/')
        self.assertEquals(response.status_code, 302, 'status_code = 302')

        response = self.client.get(
            '/api/vacant_space/?datetime_from=' + str(self.date_time_now),
            **{
                'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'not:not').decode("ascii"),
        })

        self.assertEquals(response.status_code, 403, 'status_code = 403')

    def test_reservation(self):
        workplace = WorkPlace.objects.create(name="work_test_reservation", address="address_test_reservation")
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'admin:admin').decode("ascii"),
        }
        response = self.client.post(
            '/api/reservation/')
        self.assertEquals(response.status_code, 302, 'status_code = 302')
        response = self.client.post(
            '/api/reservation/', **auth_headers)
        self.assertEquals(response.status_code, 400, 'status_code = 400')
        self.assertTrue('Not correct id' in str(response.content), 'Not correct id')
        response = self.client.post(
            '/api/reservation/?id="Q"', **auth_headers)
        self.assertEquals(response.status_code, 400, 'status_code = 400')
        self.assertTrue('Not correct id' in str(response.content), 'Not correct id')
        response = self.client.post(
            '/api/reservation/', {'id': '1', 'datetime_from': str(self.date_time_now - datetime.timedelta(minutes=1))},
            **auth_headers)
        self.assertTrue('Please, use right date format: datetime_from < date_time_now' in str(response.content),
                        'datetime_from < date_time_now')
        self.assertEquals(response.status_code, 400, 'status_code = 400')

        response = self.client.post(
            '/api/reservation/', {'id':'1', 'datetime_from':'qwerty'},
            **auth_headers)
        self.assertTrue('Please, use right date format: Unknown string format: qwerty' in str(response.content),
                        'use right date format')
        self.assertEquals(response.status_code, 400, 'status_code = 400')

        response = self.client.post(
            '/api/reservation/', {'id': '1', 'datetime_from': str(
                self.date_time_now + datetime.timedelta(minutes=2)), 'datetime_to' :str(
                self.date_time_now + datetime.timedelta(minutes=1))},
            **auth_headers)
        self.assertTrue('Please, use right date format: datetime_from < datetime_to' in str(response.content),
                        'datetime_from < datetime_to')
        self.assertEquals(response.status_code, 400, 'status_code = 400')

        response = self.client.post(
            '/api/reservation/',{'id': str(workplace.id), 'datetime_from' : str(
                self.date_time_now + datetime.timedelta(minutes=30)), 'datetime_to' : str(
                self.date_time_now + datetime.timedelta(minutes=45))},
            **auth_headers)
        self.assertEquals(response.status_code, 200, 'status_code = 200')
        self.assertTrue('Reservation created' in str(response.content), 'Reservation created')

        response = self.client.post(
            '/api/reservation/', {'id': str(workplace.id), 'datetime_from': str(
                self.date_time_now + datetime.timedelta(minutes=30)), 'datetime_to': str(
                self.date_time_now + datetime.timedelta(minutes=45))},
            **auth_headers)
        self.assertEquals(response.status_code, 400, 'status_code = 400')
        self.assertTrue('Cannot make reservation for this period of time' in str(response.content),
                        'Cannot make reservation for this period of time')
        # WorkPlace.objects.all().order_by('id').last().id+1
        response = self.client.post(
            '/api/reservation/',{'id':'0','datetime_from' : str(
                self.date_time_now + datetime.timedelta(minutes=30)), 'datetime_to' : str(
                self.date_time_now + datetime.timedelta(minutes=45))},
            **auth_headers)
        self.assertEquals(response.status_code, 400, 'status_code = 400')
        self.assertTrue('WorkPlace with this id does not exists' in str(response.content),
                        'WorkPlace with this id does not exists')

    def test_reservation_info(self):
        auth_headers = {
            'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'admin:admin').decode("ascii"),
        }
        response = self.client.get(
            '/api/reservation_info/')
        self.assertEquals(response.status_code, 302, 'status_code = 302')
        response = self.client.get(
            '/api/reservation_info/', **{
                'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'not:not').decode("ascii"),
            })
        self.assertEquals(response.status_code, 403, 'status_code = 403')
        response = self.client.get(
            '/api/reservation_info/', **{
                'HTTP_AUTHORIZATION': 'Basic ' + base64.b64encode(b'username2:Qwerty123').decode("ascii"),
            })
        self.assertEquals(response.status_code, 302, 'status_code = 302')
        response = self.client.get(
            '/api/reservation_info/?id=0', **auth_headers)
        self.assertEquals(response.status_code, 200, 'status_code = 200')
        self.assertTrue(response.content.decode("ascii") == '{"Answer": []}', '[] id=0')

        response = self.client.get(
            '/api/reservation_info/?id=1', **auth_headers)
        self.assertEquals(response.status_code, 200, 'status_code = 200')
        self.assertTrue("date_from" and 'date_to' and '"username": "username2"' in str(response.content.decode("ascii")),
                        'Reservation info')
