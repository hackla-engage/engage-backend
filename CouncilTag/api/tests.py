from django.test import TestCase
import json
from CouncilTag.injest.models import Agenda, Committee
import jwt
from CouncilTag import settings
from django.contrib.auth.models import User


# Create your tests here.
class TestAgendasEndpoint(TestCase):
    def test_response(self):
        response = self.client.get("/api/agendas.json")
        self.assertEqual(200, response.status_code)
        json_res = response.json()
        self.assertEqual([], json_res)

    def test_db(self):
        print('dfsdfsds')
        committee = Committee(name="test")
        committee.save()
        print(committee)
        self.assertEqual(1, committee.id)
        Agenda(meeting_time=393939393, committee=committee).save()
        response = self.client.get("/api/agendas.json")
        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response.json()))


class TestTagsEndpoint(TestCase):
    def test_response(self):
        response = self.client.get("/api/tags.json")
        self.assertEqual(200, response.status_code)
        from CouncilTag.injest.management.commands.populate_tags import seed_tags
        #we just want to make sure that we have atleast the seed tags in the db
        self.assertGreaterEqual(len(seed_tags), len(response.json()))

class TestLoginEndpoint(TestCase):
    
    
    def test_user_creation(self):
        user_to_test_against = User.objects.create_user("test", email="test@test.com", password='test')       
        jwt_token = jwt.encode({'user':user_to_test_against.username}, settings.SECRET_KEY)
        response = self.client.post("/api/login.json", {'email':'test@test.com', 'password': 'test'})
        token = response.json()['token']
        #have to decode the jwt_token since it will be a byte-object and not string
        self.assertEqual(jwt_token.decode('utf-8'), token)
    
    def test_user_wrong_info(self):
        user_to_test_against = User.objects.create_user("test", email="test@test.com", password='test')       
        response = self.client.post("/api/login.json", {'email':'test@test.com', 'password': 'testing'})
        self.assertEqual(404, response.status_code)




        