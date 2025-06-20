from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Post, Group

class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Описание группы'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Исходный текст поста',
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.__class__.user)

    def test_create_post(self):
        """Проверка создания нового поста при отправке валидной формы."""
        post_count_before = Post.objects.count()
        form_data = {
            'text': 'Новый тестовый пост',
            'group': self.__class__.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count_before + 1)
        new_post = Post.objects.latest('id')
        self.assertEqual(new_post.text, 'Новый тестовый пост')
        self.assertEqual(new_post.group.id, self.__class__.group.id)
        self.assertEqual(new_post.author, self.__class__.user)
        self.assertRedirects(response, reverse('posts:profile', kwargs={'username': self.__class__.user.username}))

    def test_edit_post(self):
        """Проверка редактирования поста при отправке валидной формы."""
        post_count_before = Post.objects.count()
        form_data = {
            'text': 'Обновлённый текст поста',
            'group': self.__class__.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.__class__.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count_before)
        edited_post = Post.objects.get(id=self.__class__.post.id)
        self.assertEqual(edited_post.text, 'Обновлённый текст поста')
        self.assertEqual(edited_post.group.id, self.__class__.group.id)
        self.assertEqual(edited_post.author, self.__class__.user)
        self.assertRedirects(response, reverse('posts:post_detail', kwargs={'post_id': self.__class__.post.id}))