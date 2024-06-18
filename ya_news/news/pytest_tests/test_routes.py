from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects

pytestmark = pytest.mark.django_db
ANONYMOUS_CLIENT = (pytest.lazy_fixture('anonymous_client'))
AUTHOR_CLIENT = (pytest.lazy_fixture('author_client'))
NOT_AUTHOR_CLIENT = (pytest.lazy_fixture('not_author_client'))
HOME_URL = (pytest.lazy_fixture('home_url'))
LOGIN_URL = (pytest.lazy_fixture('login_url'))
LOGOUT_URL = (pytest.lazy_fixture('logout_url'))
SIGNUP_URL = (pytest.lazy_fixture('signup_url'))
DETAIL_URL = (pytest.lazy_fixture('detail_url'))
EDIT_URL = (pytest.lazy_fixture('edit_url'))
DELETE_URL = (pytest.lazy_fixture('delete_url'))


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (DETAIL_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (SIGNUP_URL, ANONYMOUS_CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
    )
)
def test_pages_availability_for_different_user(
        url, parametrized_client, expected_status
):
    """Тест доступности страниц для разных пользователей."""
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (
        (EDIT_URL),
        (DELETE_URL),
    )
)
def test_redirect_for_anonymous_client(client, url, login_url):
    """Тест для проверки редиректа анонимного пользователя."""
    redirect_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, redirect_url)
