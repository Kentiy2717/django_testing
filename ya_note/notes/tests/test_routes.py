from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.models import Note

User = get_user_model()
SLUG = 'note-slug'
HOME_URL = reverse('notes:home')
LOGIN_URL = reverse('users:login')
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')
DETAIL_URL = reverse('notes:detail', args=(SLUG,))
EDIT_URL = reverse('notes:edit', args=(SLUG,))
DELETE_URL = reverse('notes:delete', args=(SLUG,))
LIST_URL = reverse('notes:list')
ADD_URL = reverse('notes:add')
DONE_URL = reverse('notes:success')


class TestRoutes(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст заметки',
            slug='note-slug',
            author=cls.author,
        )

    def test_pages_availability_for_anonymous_user(self):
        urls = (
            (HOME_URL, False),
            (LOGIN_URL, False),
            (SIGNUP_URL, False),
            (DETAIL_URL, True),
            (EDIT_URL, True),
            (LIST_URL, True),
            (ADD_URL, True),
            (DONE_URL, True),
            (ADD_URL, True),
            (LOGOUT_URL, False),
        )
        for url, args in urls:
            response = self.client.get(url)
            with self.subTest(url=url, args=args):
                if args:
                    expected_url = f'{LOGIN_URL}?next={url}'
                    self.assertRedirects(response, expected_url)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
     
    def test_pages_availability_for_author(self):
        urls = (
            HOME_URL,
            LOGIN_URL,
            SIGNUP_URL,
            DETAIL_URL,
            EDIT_URL,
            LIST_URL,
            ADD_URL,
            DONE_URL,
            ADD_URL,
            DELETE_URL,
            LOGOUT_URL,
        )
        for url in urls:
            response = self.author_client.get(url)
            with self.subTest(url=url):
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        urls = (
            (HOME_URL, False),
            (LOGIN_URL, False),
            (SIGNUP_URL, False),
            (DETAIL_URL, True),
            (EDIT_URL, True),
            (LIST_URL, False),
            (ADD_URL, False),
            (DONE_URL, False),
            (ADD_URL, False),
            (DELETE_URL, True),
            (LOGOUT_URL, False),
        )
        for url, args in urls:
            response = self.not_author_client.get(url)
            with self.subTest(url=url, args=args, response=response):
                if args:
                    self.assertEqual(
                        response.status_code, HTTPStatus.NOT_FOUND
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)
