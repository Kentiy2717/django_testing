from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

pytestmark = pytest.mark.django_db


def test_anonymous_user_cant_create_comment(client, form_data, detail_url):
    comments_count = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_count_now = Comment.objects.count()
    assert comments_count == comments_count_now


def test_user_can_create_comment(
    not_author_client, form_data, detail_url, news, not_author
):
    comments_count = Comment.objects.count()
    response = not_author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count_now = Comment.objects.count()
    assert comments_count_now - comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == not_author


def test_user_cant_use_bad_words(not_author_client, detail_url,):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count = Comment.objects.count()
    response = not_author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count_now = Comment.objects.count()
    assert comments_count_now - comments_count == 0


def test_author_can_delete_comment(
        author_client,
        comment,
        detail_url,
        delete_url
):
    comments_count = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, detail_url + '#comments')
    comments_count_now = Comment.objects.count()
    assert comments_count - comments_count_now == 1


def test_user_cant_delete_comment_of_another_user(
        not_author_client,
        delete_url
):
    comments_count = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_now = Comment.objects.count()
    assert comments_count == comments_count_now


def test_author_can_edit_comment(
        author_client,
        author,
        news,
        edit_url,
        form_data,
        comment,
        detail_url
):
    comments_count = Comment.objects.count()
    response = author_client.post(edit_url, data=form_data)
    assertRedirects(response, detail_url + '#comments')
    comments_count_now = Comment.objects.count()
    assert comments_count == comments_count_now
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news



def test_user_cant_edit_comment_of_another_user(
        not_author_client,
        author,
        news,
        edit_url,
        form_data,
        comment
):
    comment_text = comment.text
    comments_count = Comment.objects.count()
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_now = Comment.objects.count()
    assert comments_count == comments_count_now
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == comment_text    
    assert comment.author == author
    assert comment.news == news
