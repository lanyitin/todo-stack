# -*- coding: utf-8 -*-

import unittest
import base64
import json
from .. import app, engine
from ..libs.model import Base

class app_test(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()

    def tearDown(self):
        self.app = None
        Base.metadata.drop_all(engine)
        Base.metadata.create_all(engine)

    def test_first_visit_should_redirect_to_login_page(self):
        response = self.app.get('/')
        self.assertEquals('302 FOUND', response.status);
        self.assertTrue('login' in response.headers['Location']);

    def test_register(self):
        response = self.app.post(
            '/register/',
            data={'username': 'lanyitin', 'password': 'password', 'email': 'test@domain.name'}
        )
        api_key = base64.encodestring('lanyitin;password')
        response = self.app.get('/?api_key='+api_key)
        self.assertEquals('200 OK', response.status)

    def test_push(self):
        response = self.app.post(
            '/register/',
            data={'username': 'lanyitin', 'password': 'password', 'email': 'test@domain.name'}
        )
        api_key = base64.encodestring('lanyitin;password')
        response = self.app.get('/?api_key='+api_key)
        self.assertEquals('200 OK', response.status)
        api_key = base64.encodestring('lanyitin;password')
        data = {'item': 'Jesse', 'required_clock': 3, 'priority': 2, 'api_key': api_key}
        response = self.app.post('/push/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)
        response = response[0]
        self.assertEquals('Jesse', response['content'])
        self.assertEquals(2, response['priority'])
        self.assertEquals(3, response['required_clock'])
        self.assertEquals(0, response['order'])
