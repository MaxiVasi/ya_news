# В файле test_routes.py:
# + Главная страница доступна анонимному пользователю.
# + Страница отдельной новости доступна анонимному пользователю.
# + Страницы удаления и редактирования комментария доступны автору комментария.
# + При попытке перейти на страницу редактирования или удаления комментария
# + анонимный пользователь перенаправляется на страницу авторизации.
# + Авторизованный пользователь не может зайти на страницы редактирования
# + или удаления чужих комментариев (возвращается ошибка 404).
# + Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.

from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse

CLIENT = pytest.lazy_fixture('client')
AUTHOR = pytest.lazy_fixture('author_client')
NOT_AUTHOR = pytest.lazy_fixture('not_author_client')
HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
EDIT_URL = pytest.lazy_fixture('edit_url')
DELETE_URL = pytest.lazy_fixture('delete_url')
USER_LOGIN = pytest.lazy_fixture('user_login_url')
USER_LOGOUT = pytest.lazy_fixture('user_logout_url')
USER_SIGNUP = pytest.lazy_fixture('user_signup_url')


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, status',
    (
        (HOME_URL, CLIENT, HTTPStatus.OK),
        (DETAIL_URL, CLIENT, HTTPStatus.OK),
        (USER_LOGIN, CLIENT, HTTPStatus.OK),
        (USER_LOGOUT, CLIENT, HTTPStatus.OK),
        (USER_SIGNUP, CLIENT, HTTPStatus.OK),
        (EDIT_URL, AUTHOR, HTTPStatus.OK),
        (DELETE_URL, AUTHOR, HTTPStatus.OK),
        (EDIT_URL, NOT_AUTHOR, HTTPStatus.NOT_FOUND),
        (DELETE_URL, NOT_AUTHOR, HTTPStatus.NOT_FOUND),
    ),
)
def test_global_respond_status_check(reverse_url, parametrized_client, status):
    """Глобальная проверка доступности страниц."""
    response = parametrized_client.get(reverse_url)
    assert response.status_code == status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'reverse_url, parametrized_client, user_url',
    (
        (EDIT_URL, CLIENT, USER_LOGIN),
        (DELETE_URL, CLIENT, USER_LOGIN),
    ),
)
def test_global_redirect_check(reverse_url, parametrized_client, user_url):
    """Глобальная проверка редиректа пользователей."""
    expected_url = f'{user_url}?next={reverse_url}'
    response = parametrized_client.get(reverse_url)
    assertRedirects(response, expected_url)


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client, home_url):
    """Доступность главной страницы для неавторизинованного пользователя."""
    response = client.get(home_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_pages_availability_for_anonymous_user(client, detail_url):
    """Страница отдельной новости доступна анонимному пользователю."""
    response = client.get(detail_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:logout', 'users:signup')
)
def test_pages_availability_for_anonymous_user(client, name):
    """Доступность страниц авторизации для неавторизинованного пользователя."""
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page',
    ('news:edit', 'news:delete')
)
def test_pages_edit_delete_for_anonymous_user(client, comment, page):
    """Анонимный пользователь редиректится на страницу авторизации."""
    url = reverse(page, args=(comment.pk,))
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'page',
    ('news:edit', 'news:delete')
)
def test_pages_edit_delete_for_author_user(author_client, comment, page):
    """Автор может заходить на страницы edit и delete своих комментариев."""
    url = reverse(page, args=(comment.pk,))
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page',
    ('news:edit', 'news:delete')
)
def test_edit_delete_for_not_author_user(not_author_client, comment, page):
    """Пользователь не может редактировать чужие записи."""
    url = reverse(page, args=(comment.pk,))
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
