# В файле test_routes.py:
# + Главная страница доступна анонимному пользователю.
# + Страница отдельной новости доступна анонимному пользователю.
# + Страницы удаления и редактирования комментария доступны автору комментария.
# + При попытке перейти на страницу редактирования или удаления комментария
# + анонимный пользователь перенаправляется на страницу авторизации.
# + Авторизованный пользователь не может зайти на страницы редактирования
# + или удаления чужих комментариев (возвращается ошибка 404).
# + Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.

import pytest
from pytest_django.asserts import assertRedirects

from django.urls import reverse

from http import HTTPStatus


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    """Доступность главной страницы для неавторизинованного пользователя."""
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_news_pages_availability_for_anonymous_user(client, pk_for_one_news):
    """Страница отдельной новости доступна анонимному пользователю."""
    url = reverse('news:detail', args=pk_for_one_news)
    response = client.get(url)
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
def test_pages_edit_delete_for_anonymous_user(client, pk_comment, page):
    """Анонимный пользователь редиректится на страницу авторизации."""
    url = reverse(page, args=pk_comment)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)


@pytest.mark.parametrize(
    'page',
    ('news:edit', 'news:delete')
)
def test_pages_edit_delete_for_author_user(author_client, pk_comment, page):
    """Автор может заходить на страницы edit и delete своих комментариев."""
    url = reverse(page, args=pk_comment)
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
@pytest.mark.parametrize(
    'page',
    ('news:edit', 'news:delete')
)
def test_edit_delete_for_not_author_user(not_author_client, pk_comment, page):
    """Анонимный пользователь редиректится на страницу авторизации."""
    url = reverse(page, args=pk_comment)
    response = not_author_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
