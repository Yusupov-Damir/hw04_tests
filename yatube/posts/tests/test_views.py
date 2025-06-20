from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase, Client
from django import forms

from ..models import Group, Post

User = get_user_model()

class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём пользователя
        cls.user = User.objects.create_user(username='testuser', password='testpass123')
        # Создаём группы
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание'
        )
        # Создадим запись пост
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост для проверки URL',
            group=cls.group
        )

        # Добавим 12 тестовых постов для проверки пагинатора (итого 13)
        for i in range(12):
            Post.objects.create(
                author=cls.user,
                text=f'Пост {i}',
                group=cls.group
            )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент:
        self.authorized_client = Client()
        # Авторизуем пользователя:
        # force_login - стандартный метод имитации авторизации пользователя
        self.authorized_client.force_login(self.__class__.user)  # __class__ используем польз-ля из setUpClass

    # Задание 1: проверка namespace:name
    def test_urls_uses_correct_template(self):
        """view-функциях используются правильные html-шаблоны."""
        # URL-адреса и соответствующие шаблоны
        urls_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': self.__class__.group.slug}): 'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.__class__.user.username}): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': self.__class__.post.id}): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': self.__class__.post.id}): 'posts/create_post.html',
        }
        for url, template in urls_templates_names.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    # Задание2: Тесты для пагинатора
    def test_index_first_page_contains_ten_records(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_index_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_group_list_first_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.__class__.group.slug}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_group_list_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.__class__.group.slug}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    def test_profile_first_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.__class__.user.username}))
        self.assertEqual(len(response.context['page_obj']), 10)

    def test_profile_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.__class__.user.username}) + '?page=2')
        self.assertEqual(len(response.context['page_obj']), 3)

    # Тесты для контекста
    def test_index_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        posts = response.context['page_obj']  # Берем все посты на странице
        self.assertTrue(any(post.text == 'Тестовый пост для проверки URL' for post in posts))
        self.assertTrue(any(post.author == self.__class__.user for post in posts))
        self.assertTrue(any(post.group == self.__class__.group for post in posts))

    def test_group_list_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.__class__.group.slug}))
        posts = response.context['page_obj']
        self.assertTrue(any(post.text == 'Тестовый пост для проверки URL' for post in posts))
        self.assertTrue(any(post.author == self.__class__.user for post in posts))
        self.assertTrue(any(post.group == self.__class__.group for post in posts))

    def test_profile_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.__class__.user.username}))
        posts = response.context['page_obj']
        self.assertTrue(any(post.text == 'Тестовый пост для проверки URL' for post in posts))
        self.assertTrue(any(post.author == self.__class__.user for post in posts))
        self.assertTrue(any(post.group == self.__class__.group for post in posts))

    def test_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.__class__.post.id}))
        self.assertEqual(response.context['post'].text, 'Тестовый пост для проверки URL')
        self.assertEqual(response.context['post'].author, self.__class__.user)
        self.assertEqual(response.context['post'].group, self.__class__.group)

    def test_create_post_show_correct_context_new(self):
        """Шаблон create_post для создания сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context_edit(self):
        """Шаблон create_post для редактирования сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.__class__.post.id}))
        form_fields = {
            'text': forms.CharField,
            'group': forms.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertEqual(response.context['form'].instance, self.__class__.post)
