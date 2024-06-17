from pytils.translit import slugify
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.test.client import Client
from django.urls import reverse

from notes.forms import WARNING
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


class TestLogicCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        assert Note.objects.count() == 0
        response = self.author_client.post(ADD_URL, data=self.form_data)
        assertRedirects(response, DONE_URL)
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        assert new_note.title == self.form_data['title']
        assert new_note.text == self.form_data['text']
        assert new_note.slug == self.form_data['slug']
        assert new_note.author == self.author

    def test_anonymous_user_cant_create_note(self):
        note_count = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.form_data)
        expected_url = f'{LOGIN_URL}?next={ADD_URL}'
        assertRedirects(response, expected_url)
        assert Note.objects.count() == note_count

    def test_empty_slug(self):
        self.form_data.pop('slug')
        assert Note.objects.count() == 0
        response = self.author_client.post(ADD_URL, data=self.form_data)
        assertRedirects(response, DONE_URL)
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug
        assert new_note.title == self.form_data['title']
        assert new_note.text == self.form_data['text']
        assert new_note.author == self.author


class TestLogicEdit(TestCase):

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
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_not_unique_slug(self):
        assert Note.objects.count() == 1
        self.form_data['slug'] = self.note.slug
        response = self.author_client.post(ADD_URL, data=self.form_data)
        assertFormError(response, 'form', 'slug', errors=(
            self.note.slug + WARNING
        ))
        assert Note.objects.count() == 1

    def test_author_can_edit_note(self):
        assert Note.objects.count() == 1
        response = self.author_client.post(EDIT_URL, self.form_data)
        assertRedirects(response, DONE_URL)
        self.note.refresh_from_db()
        assert self.note.title == self.form_data['title']
        assert self.note.text == self.form_data['text']
        assert self.note.slug == self.form_data['slug']
        assert self.note.author == self.author

    def test_other_user_cant_edit_note(self):
        assert Note.objects.count() == 1
        response = self.not_author_client.post(EDIT_URL, self.form_data)
        assert Note.objects.count() == 1
        assert response.status_code == HTTPStatus.NOT_FOUND
        note_from_db = Note.objects.get(id=self.note.id)
        assert self.note.title == note_from_db.title
        assert self.note.text == note_from_db.text
        assert self.note.slug == note_from_db.slug

    def test_author_can_delete_note(self):
        note_count = Note.objects.count()
        response = self.author_client.post(DELETE_URL)
        assertRedirects(response, DONE_URL)
        assert Note.objects.count() - note_count == -1

    def test_other_user_cant_delete_note(self):
        note_count = Note.objects.count()
        response = self.not_author_client.post(DELETE_URL)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Note.objects.count() == note_count
