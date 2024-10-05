# В файле test_logic.py:
# + Анонимный пользователь не может отправить комментарий.
# + Авторизованный пользователь может отправить комментарий.
# + Если комментарий содержит запрещённые слова,
# + он не будет опубликован, а форма вернёт ошибку.
# Авторизованный пользователь может редактировать или удалять свои комментарии.
# Авторизованный пользователь не может редактировать или удалять чужие комментарии.

import pytest
from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

NEW_COMMENT_TEXT = 'Совсем новый текст комментария'


@pytest.mark.django_db
def test_anonymous_cant_create_comment(client, form_data, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_author_can_create_comment(author_client, form_data, detail_url):
    """Авторизованный пользователь может создать комментарий."""
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован"""
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING,
    )
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_author_can_edit_comment(comment, author_client, edit_url, detail_url):
    """Проверим, что редактировать комментарии может только их автор."""
    new_data = {'text': NEW_COMMENT_TEXT}
    response = author_client.post(edit_url, data=new_data)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == NEW_COMMENT_TEXT


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, detail_url, delete_url):
    """Авторизованный пользователь может удалять свой комментарий."""
    response = author_client.delete(delete_url)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


@pytest.mark.django_db
def test_not_author_cant_edit_comment_of_author_user(
        comment, not_author_client, edit_url, form_data):
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.django_db
def test_not_author_cant_delete_comment_of_author_user(not_author_client,
                                                       delete_url):
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1
