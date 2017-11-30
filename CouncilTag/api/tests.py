from django.test import TestCase
import json
from CouncilTag.injest.models import Agenda, Committee
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