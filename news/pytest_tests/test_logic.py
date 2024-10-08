# В файле test_logic.py:
# + Анонимный пользователь не может отправить комментарий.
# + Авторизованный пользователь может отправить комментарий.
# + Если комментарий содержит запрещённые слова,
# + он не будет опубликован, а форма вернёт ошибку.
# Авторизованный пользователь может редактировать или удалять свои комментарии.
# Авторизованный пользователь не может редактировать или удалять чужие комментарии.

from http import HTTPStatus

from pytest_django.asserts import assertFormError, assertRedirects

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

NEW_COMMENT_TEXT = 'Совсем новый текст комментария'
form_data = {'text': 'Новый текст комментария'}


def test_anonymous_cant_create_comment(client, detail_url):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before


def test_author_can_create_comment(author, author_client, detail_url):
    """Авторизованный пользователь может создать комментарий."""
    Comment.objects.all().delete
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author


def test_user_cant_use_bad_words(author_client, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован"""
    comments_count_before = Comment.objects.count()
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(detail_url, data=bad_words_data)
    assert Comment.objects.count() == comments_count_before
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING,
    )


def test_author_can_edit_comment(comment,
                                 author, author_client, edit_url, detail_url):
    """Проверим, что редактировать комментарии может только их автор."""
    new_data = {'text': NEW_COMMENT_TEXT}
    response = author_client.post(edit_url, data=new_data)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == new_data['text']
    assert new_comment.author == comment.author


def test_author_can_delete_comment(author_client, detail_url, delete_url):
    """Авторизованный пользователь может удалять свой комментарий."""
    comments_count_before = Comment.objects.count()
    response = author_client.delete(delete_url)
    url_to_comments = detail_url + '#comments'
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before - 1


def test_not_author_cant_edit_comment_of_author_user(
        comment, not_author_client, edit_url):
    response = not_author_client.post(edit_url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    new_comment = Comment.objects.get(pk=comment.pk)
    assert new_comment.text == comment.text
    assert new_comment.author == comment.author


def test_not_author_cant_delete_comment_of_author_user(not_author_client,
                                                       delete_url):
    comments_count_before = Comment.objects.count()
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments_count_before
