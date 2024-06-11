from pytils.translit import slugify
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestLogicCreate(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.url = reverse('notes:add')
        cls.form_data = {
            'title': 'Новый заголовок',
            'text': 'Новый текст',
            'slug': 'new-slug'
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        assert new_note.title == self.form_data['title']
        assert new_note.text == self.form_data['text']
        assert new_note.slug == self.form_data['slug']
        assert new_note.author == self.author

    def test_anonymous_user_cant_create_note(self):
        response = self.client.post(self.url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.url}'
        assertRedirects(response, expected_url)
        assert Note.objects.count() == 0

    def test_empty_slug(self):
        self.form_data.pop('slug')
        self.client.force_login(self.author)
        response = self.client.post(self.url, data=self.form_data)
        assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 1
        new_note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        assert new_note.slug == expected_slug


class TestLogicEdit(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
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
        url = reverse('notes:add')
        self.form_data['slug'] = self.note.slug
        self.client.force_login(self.author)
        response = self.client.post(url, data=self.form_data)
        assertFormError(response, 'form', 'slug', errors=(
            self.note.slug + WARNING
        ))
        assert Note.objects.count() == 1

    def test_author_can_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url, self.form_data)
        assertRedirects(response, reverse('notes:success'))
        self.note.refresh_from_db()
        assert self.note.title == self.form_data['title']
        assert self.note.text == self.form_data['text']
        assert self.note.slug == self.form_data['slug']

    def test_other_user_cant_edit_note(self):
        url = reverse('notes:edit', args=(self.note.slug,))
        self.client.force_login(self.not_author)
        response = self.client.post(url, self.form_data)
        assert response.status_code == HTTPStatus.NOT_FOUND
        note_from_db = Note.objects.get(id=self.note.id)
        assert self.note.title == note_from_db.title
        assert self.note.text == note_from_db.text
        assert self.note.slug == note_from_db.slug

    def test_author_can_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.author)
        response = self.client.post(url)
        assertRedirects(response, reverse('notes:success'))
        assert Note.objects.count() == 0

    def test_other_user_cant_delete_note(self):
        url = reverse('notes:delete', args=(self.note.slug,))
        self.client.force_login(self.not_author)
        response = self.client.post(url)
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Note.objects.count() == 1
