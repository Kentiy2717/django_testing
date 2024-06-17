from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        ((pytest.lazy_fixture('home_url')),
         (pytest.lazy_fixture('anonymous_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('detail_url')),
         (pytest.lazy_fixture('anonymous_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('login_url')),
         (pytest.lazy_fixture('anonymous_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('logout_url')),
         (pytest.lazy_fixture('anonymous_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('signup_url')),
         (pytest.lazy_fixture('anonymous_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('edit_url')),
         (pytest.lazy_fixture('author_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('delete_url')),
         (pytest.lazy_fixture('author_client')),
         HTTPStatus.OK),
        ((pytest.lazy_fixture('edit_url')),
         (pytest.lazy_fixture('not_author_client')),
         HTTPStatus.NOT_FOUND),
        ((pytest.lazy_fixture('delete_url')),
         (pytest.lazy_fixture('not_author_client')),
         HTTPStatus.NOT_FOUND),
    )
)
def test_aaaaaaaaaaaaa(url, parametrized_client, expected_status):
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        ((pytest.lazy_fixture('edit_url'))),
        ((pytest.lazy_fixture('delete_url'))),
    )
)
def test_redirect_for_anonymous_client(client, url, login_url):
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
