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

    def test_register_same_username_again_should_fail(self):
        self.test_register()
        response = self.app.post(
            '/register/',
            data={'username': 'lanyitin', 'password': 'password', 'email': 'test@domain.name'}
        )
        self.assertEquals('302 FOUND', response.status)

    def test_push(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        data = {'item': 'Jesse', 'required_clock': 3, 'priority': 2, 'api_key': api_key}
        response = self.app.post('/push/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)
        response = response[0]
        self.assertEquals('Jesse', response['content'])
        self.assertEquals(2, response['priority'])
        self.assertEquals(3, response['required_clock'])
        self.assertEquals(0, response['order'])

    def test_push_again(self):
        self.test_push()
        api_key = base64.encodestring('lanyitin;password')
        data = {'item': 'Test2', 'required_clock': 3, 'priority': 2, 'api_key': api_key}
        response = self.app.post('/push/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)
        response = response[0]
        self.assertEquals('Test2', response['content'])
        self.assertEquals(2, response['priority'])
        self.assertEquals(3, response['required_clock'])
        self.assertEquals(1, response['order'])

    def test_append(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        data = {'item': 'Jesse', 'required_clock': 3, 'priority': 2, 'api_key': api_key}
        response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)
        response = response[0]
        self.assertEquals('Jesse', response['content'])
        self.assertEquals(2, response['priority'])
        self.assertEquals(3, response['required_clock'])
        self.assertEquals(0, response['order'])

    def test_append_again(self):
        self.test_append()
        api_key = base64.encodestring('lanyitin;password')
        data = {'item': 'Test2', 'required_clock': 3, 'priority': 2, 'api_key': api_key}
        response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)
        response0 = response[0]
        self.assertEquals('Jesse', response0['content'])
        self.assertEquals(2, response0['priority'])
        self.assertEquals(3, response0['required_clock'])
        self.assertEquals(1, response0['order'])
        response1 = response[1]
        self.assertEquals('Test2', response1['content'])
        self.assertEquals(2, response1['priority'])
        self.assertEquals(3, response1['required_clock'])
        self.assertEquals(0, response1['order'])

    def test_pop(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        data = {'item': 'Test2', 'required_clock': 3, 'priority': 2, 'api_key': api_key}
        response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)
        response = response[0]
        response = self.app.get('/moveToTrash/' + str(response['id']) + '/?api_key=' + api_key)
        response = json.loads(response.data)
        response = response[0]
        self.assertEquals(True, response['in_trash'])
        self.assertEquals('Test2', response['content'])

    def test_move_from_high_to_low(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        for i in range(3):
            data = {'item': 'Test' + str(i), 'required_clock': 3, 'priority': 2, 'api_key': api_key}
            response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')


        response = self.app.get('/moveItem/2/0/?api_key=' + api_key)
        response = json.loads(response.data)
        for todo in response:
            if todo['order'] is 0:
                self.assertEquals('Test0', todo['content'])
            elif todo['order'] is 1:
               self.assertEquals('Test2', todo['content'])
            else:
               self.assertEquals('Test1', todo['content'])

    def test_remove_item(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        response = None
        for i in range(3):
            data = {'item': 'Test' + str(i), 'required_clock': 3, 'priority': 2, 'api_key': api_key}
            response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)[0]
        self.assertEquals('Test0', response['content'])
        response = self.app.get('/removeItem/' + str(response['id']) + '/?api_key=' + api_key)
        response = json.loads(response.data)[0]
        self.assertEquals('Test0', response['content'])

    def test_clean_trash(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        response = None
        for i in range(3):
            data = {'item': 'Test' + str(i), 'required_clock': 3, 'priority': 2, 'api_key': api_key}
            response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')
            response = json.loads(response.data)
            response = response[0]
            response = self.app.get('/moveToTrash/' + str(response['id']) + '/?api_key=' + api_key)

        response = self.app.get('/clean_trash/?api_key=' + api_key)
        response = json.loads(response.data)[0]
        self.assertEquals('Test0', response['content'])

    def test_raise_priority(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        response = None
        for i in range(3):
            data = {'item': 'Test' + str(i), 'required_clock': 3, 'priority': 2, 'api_key': api_key}
            response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')
        response = json.loads(response.data)[0]
        response = self.app.get('/raisePriority/' + str(response['id']) + '/?api_key=' + api_key)
        response = json.loads(response.data)[0]
        self.assertEquals(3, response['priority'])

    def test_increase_consumed_clock(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        response = None
        for i in range(3):
            data = {'item': 'Test' + str(i), 'required_clock': 3, 'priority': 2, 'api_key': api_key}
            response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')

        response = json.loads(response.data)[0]
        self.assertEquals(0, response['consumed_clock'])
        response = self.app.get('/consume/' + str(response['id']) + '/?api_key=' + api_key)
        response = json.loads(response.data)[0]
        self.assertEquals(1, response['consumed_clock'])

    def test_add_extend_clock(self):
        self.test_register()
        api_key = base64.encodestring('lanyitin;password')
        response = None
        for i in range(3):
            data = {'item': 'Test' + str(i), 'required_clock': 3, 'priority': 2, 'api_key': api_key}
            response = self.app.post('/append/', data=json.dumps(data), content_type='application/json')

        response = json.loads(response.data)[0]
        self.assertEquals(0, response['extended_clock'])
        response = self.app.get('/add_extended_clock/' + str(response['id']) + '/2/?api_key=' + api_key)
        response = json.loads(response.data)[0]
        self.assertEquals(2, response['extended_clock'])

