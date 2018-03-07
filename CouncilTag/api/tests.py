from django.test import TestCase
import json
from CouncilTag.ingest.models import Agenda, Committee, Tag, AgendaItem, EngageUserProfile
import jwt
from CouncilTag import settings
from django.contrib.auth.models import User


# Create your tests here.
class TestAgendasEndpoint(TestCase):


    def test_response(self):
        response = self.client.get("/api/agendas.json")
        self.assertEqual(200, response.status_code)
        json_res = response.json()
        self.assertEqual([], json_res['results'])

    def test_db(self):
        print('dfsdfsds')
        committee = Committee(name="test")
        committee.save()
        print(committee)
        Agenda(meeting_time=393939393, committee=committee).save()
        response = self.client.get("/api/agendas.json")
        self.assertEqual(200, response.status_code)
        result_dict = response.json()
        self.assertEqual(1, len(result_dict['results']))


class TestTagsEndpoint(TestCase):
    def test_response(self):
        response = self.client.get("/api/tags.json")
        self.assertEqual(200, response.status_code)
        from CouncilTag.ingest.management.commands.populate_tags import seed_tags
        #we just want to make sure that we have atleast the seed tags in the db
        self.assertGreaterEqual(len(seed_tags), len(response.json()))

class TestLoginEndpoint(TestCase):
    
    
    def test_user_creation(self):
        user_to_test_against = User.objects.create_user("test", email="test@test.com", password='test')       
        jwt_token = jwt.encode({'email':user_to_test_against.email}, settings.SECRET_KEY)
        response = self.client.post("/api/login.json", {'email':'test@test.com', 'password': 'test'})
        token = response.json()['token']
        #have to decode the jwt_token since it will be a byte-object and not string
        self.assertEqual(jwt_token.decode('utf-8'), token)
    
    def test_user_wrong_info(self):
        user_to_test_against = User.objects.create_user("test", email="test@test.com", password='test')       
        response = self.client.post("/api/login.json", {'email':'test@test.com', 'password': 'testing'})
        self.assertEqual(404, response.status_code)


    def test_user_signup(self):
        user_info = {
            "name": "Test Testman",
            "email": "test@test.com",
            "password": "test"
        }
        response = self.client.post("/api/signup.json", user_info )
        self.assertEqual(201, response.status_code)
        user = User.objects.get(email="test@test.com")
        self.assertEqual(user_info['email'], user.email)

class TestAgendasByTagEndpoint(TestCase):
    def test_response(self):
        tag = Tag(name="Test")
        tag.save()
        committee = Committee(name="Council")
        committee.save()
        agenda = Agenda(meeting_time=949494949, committee=committee)
        agenda.save()
        agenda_item = AgendaItem(title="test", department="test", agenda=agenda )
        agenda_item.save()
        agenda_item.tags.add(tag)
        agenda_item.save()
        response = self.client.get("/api/tag/Test/agenda/items.json")
        self.assertEqual(200, response.status_code)
        self.assertEqual("Test", response.json()['tag'])
        self.assertEqual(1, len(response.json()['items']))
        self.assertEqual("test", response.json()['items'][0]['title'])


class TestSendMessageEndpoint(TestCase):
    def setUp(self):
        user = User.objects.create_user("test", email="test@test.com", password="test")

        engage_user = EngageUserProfile(user=user).save()

    def test_response(self):
        self.client.login(username="test@test.com", password="test")
        response = self.client.post("/api/send/message/")
        self.assertEqual(200, response.status_code)

    