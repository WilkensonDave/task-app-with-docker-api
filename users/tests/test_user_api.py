from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient



CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse("user:token")
ME_URL = reverse("user:me")

def create_user(**params):
    """Create and return new user"""
    return get_user_model().objects.create_user(**params)


class RegisterUserTestCase(APITestCase):
    """Test to register a new user and to test the public features of the API"""

    def test_register_user(self):
        data ={
            "username":"Dave",
            "email":"dave@gmail.com",
            "password":"dave@1234"
        }

        res = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=data['email'])
        self.assertTrue(user.check_password(data['password']))
        self.assertNotIn('password', res.data)

    def test_user_with_existing_email_error(self):
        """test to return an error if email already exists."""
        data ={
            "email":"dave@gmail.com",
            "password":"example123",
            "username":"Bob"
        }

        create_user(**data)
        res = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Return an error if the password is less than 8 characters."""

        data ={
            "username":"Dave",
            "email":"dave@example.com",
            "password":"dave"
        }

        res = self.client.post(CREATE_USER_URL, data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=data['email']
        ).exists()

        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """test to create token for user with valid credentials"""
        user_details ={
            "username":"Son",
            "password":"son#$3546",
            "email":"son@example.com"
        }

        create_user(**user_details)
        data = {
            "email":user_details['email'],
            "password":user_details['password']
        }

        res = self.client.post(TOKEN_URL, data)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_token_for_bad_creadential(self):
        """Test to return error if user provided bad credentials."""
        create_user(email="dave@example.com", password="dave$%1234", username="dave")
        data = {
            "email":"dave@example.com",
            "password":"dave$@1234",
            "username":"dave"
        }

        res = self.client.post(TOKEN_URL, data)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_token_for_bad_password(self):
        """Test to return an error if password is blank"""
        data ={
            "username":"Son",
            "password":"",
            "email":"son@example.com"
        }

        res = self.client.post(TOKEN_URL, data)
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_user(self):
        """Test to retrieve a user"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateUserAPIDataTests(APITestCase):
    """Test api that will require authentication to access them."""

    def setUp(self):
        self.user = create_user(
            email="dave@example.com",
            username="dave",
            password="dave@3412"
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_update_user_profile_success(self):
        """Test to update user profile if user is authenticated"""
        data = {
            "username":"Davelove",
            "password":"davelove@123"
        }

        res = self.client.patch(ME_URL, data)
        self.user.refresh_from_db()
        self.assertEqual(self.user.username, data['username'])
        self.assertTrue(self.user.check_password(data["password"]))
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_user_success(self):
        """Test to retrieve user profile"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            "username":self.user.username,
            "email":self.user.email
        })

    def test_post_request_not_allowed_for_me_url(self):
        """Test to throw error for a post to the me url"""
        res = self.client.post(ME_URL, {})
        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)









