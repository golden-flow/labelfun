import unittest

from flask import url_for, current_app
from labelfun import create_app, db
from labelfun.models import User
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from labelfun.settings import config


class AuthTestCase(unittest.TestCase):

    def setUp(self):
        app = create_app('testing')
        app.config.from_object(config['testing'])
        app.testing = True
        self.app_context = app.test_request_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.client = app.test_client()
        user = User(id=1001, name='User', password='12345678',
                    email='user@email.com', type='user')
        user2 = User(id=1002, name='New User', password=r'!@#$%^&*',
                     email='newuser@email.com', type='user')
        admin = User(id=2001, name='Admin', password='abcdefgh',
                     email='admin@email.com', type='admin')
        db.session.add(user)
        db.session.add(user2)
        db.session.add(admin)
        db.session.commit()

    def tearDown(self):
        db.drop_all()
        self.app_context.pop()

    def test_login(self):
        num_users = User.query.count()
        response = self.client.post(
            url_for('api.auth.login'),
            json=dict(
                email='user@email.com',
                password='12345678',
                grant_type="password"
            ),
            headers=self.set_headers()
        )
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['email'], 'user@email.com')
        self.assertEqual(data['type'], 'user')
        self.assertEqual(data['token_type'], 'Bearer')
        token = data['access_token']
        s = Serializer(current_app.config['SECRET_KEY'])
        token_id = s.loads(token)['id']
        self.assertEqual(token_id, 1001)

    def test_get_user_user_success(self):
        token = self.get_auth_token('user@email.com', '12345678')
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['name'], 'User')
        self.assertEqual(data['email'], 'user@email.com')
        self.assertEqual(data['type'], 'user')

    def test_get_user_admin_success(self):
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['id'], 1001)
        self.assertEqual(data['name'], 'User')
        self.assertEqual(data['email'], 'user@email.com')
        self.assertEqual(data['type'], 'user')

    def test_get_user_fail(self):
        token = self.get_auth_token('user@email.com', '12345678')
        response = self.client.get(
            url_for('api.user.user', user_id=2001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 403)

    def test_create_user(self):
        response = self.client.post(
            url_for('api.user.users'), headers=self.set_headers(), json=dict(
                name="Another User",
                email="another@email.com",
                password="abcdefg1234'"
            )
        )
        self.assertEqual(response.status_code, 201)
        id = response.get_json()['id']
        token = self.get_auth_token('another@email.com', 'abcdefg1234\'')
        response = self.client.get(
            url_for('api.user.user', user_id=id),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['name'], 'Another User')

    def test_patch_user_user_success(self):
        token = self.get_auth_token('user@email.com', '12345678')
        response = self.client.patch(
            url_for('api.user.user', user_id=1001), headers=self.set_headers(token), json=dict(
                name="New Name",
                old_password="12345678"
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.patch(
            url_for('api.user.user', user_id=1001), headers=self.set_headers(token), json=dict(
                email="newemail@email.com",
                new_password="123467abcd5'",
                old_password="12345678"
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'newemail@email.com')
        self.assertEqual(data['name'], 'New Name')
        self.get_auth_token("newemail@email.com", "123467abcd5'")

    def test_patch_user_admin_success(self):
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.patch(
            url_for('api.user.user', user_id=1001), headers=self.set_headers(token), json=dict(
                name="New Name",
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.patch(
            url_for('api.user.user', user_id=1001), headers=self.set_headers(token), json=dict(
                email="newemail@email.com",
                new_password="123467abcd5'",
            )
        )
        self.assertEqual(response.status_code, 200)
        response = self.client.get(
            url_for('api.user.user', user_id=1001),
            headers=self.set_headers(token)
        )
        self.assertEqual(response.status_code, 200)
        data = response.get_json()
        self.assertEqual(data['email'], 'newemail@email.com')
        self.assertEqual(data['name'], 'New Name')
        self.get_auth_token("newemail@email.com", "123467abcd5'")

    def test_patch_user_duplicate_email_fail(self):
        token = self.get_auth_token('admin@email.com', 'abcdefgh')
        response = self.client.patch(
            url_for('api.user.user', user_id=1001), headers=self.set_headers(token), json=dict(
                email="newuser@email.com"
            )
        )
        self.assertEqual(response.status_code, 400)
        error_msg = response.get_json()['message']
        self.assertEqual(error_msg, 'DUPLICATED_EMAIL')

    def get_auth_token(self, email, password):
        response = self.client.post(url_for('api.auth.login'), json=dict(
            email=email,
            password=password,
            grant_type="password"
        ))
        return response.get_json()['access_token']

    def set_headers(self, token=None):
        if token is None:
            return {
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
        else:
            return {
                'Authorization': 'Bearer ' + token,
                'Accept': 'application/json',
                'Content-Type': 'application/json'
            }
