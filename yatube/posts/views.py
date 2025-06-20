from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .models import Post, Group
from .forms import PostForm

User = get_user_model()


def index(request):
    post_list = Post.objects.all().order_by('-pub_date')  # Запрос к модели.
    paginator = Paginator(post_list, 10)  # Показывать по 10 записей на странице.
    page_number = request.GET.get('page')  # Из URL извлекаем номер запрошенной страницы - page.
    page_obj = paginator.get_page(page_number)  # Получаем набор записей для страницы с запрошенным номером.
    return render(request, 'posts/index.html', {'page_obj': page_obj})

def group_posts(request, slug):  # Принимаем в аргументе переменную slug из URL.
    group = get_object_or_404(Group, slug=slug)  # Берем объект модели Group, у которого поле slug = перем-ой.
    post_list = Post.objects.all().filter(group=group).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'group': group,
        'page_obj': page_obj,
    }
    return render(request, 'posts/group_list.html', context)

def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts_count = Post.objects.filter(author=user).count()
    post_list = Post.objects.all().filter(author=user).order_by('-pub_date')
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'posts/profile.html', {
        'profile': user,
        'page_obj': page_obj,
        'posts_count': posts_count,
    })

def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    posts_count = Post.objects.filter(author=post.author).count()
    return render(request, 'posts/post_detail.html', {
        'post': post,
        'posts_count': posts_count
    })

@login_required  # Создание поста только для авторизованных польз-ей.
def post_create(request):
    """
    1. Метод form.save() — создаёт объект модели (Post) на основе данных формы.
    Параметр commit=False: "Создай объект, но не сохраняй его в базу данных сразу".
    Эта строка нужна что бы далее добавить к объекту поле, которого нет в форме.
    2. Поле author объекта post. Объект request.user — это текущий
    авторизованный пользователь, который доступен благодаря декоратору @login_required.
    И так как в модели Post поле author определено как ForeignKey к модели User,
    значит поле author должно содержать объект модели User, а не строку с именем.
    """
    groups = Group.objects.all()  # Получаем группы для выпадающего меню в шаблоне.

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            text = form.cleaned_data['text']
            group = form.cleaned_data['group']
            post = form.save(commit=False)  # 1.
            post.author = request.user  # 2.
            post.save()  # Cохраняет объект post в базу данных.
            return redirect('posts:profile', username=request.user.username)
        return render(request, 'posts/create_post.html', {'form': form, 'groups': groups})

    form = PostForm()
    return render(request, 'posts/create_post.html', {'form': form, 'groups': groups})

@login_required  # Редактирование поста только для автор-ых пользователей.
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)  # Запрашиваем объект модели Post - редактируемый пост.
    groups = Group.objects.all()
    is_edit = True  # Переменная нужна так как мы используем один шаблон для двух эндпоинтов.

    if post.author != request.user:  # Проверяем, является ли текущий пользователь автором.
        return redirect('posts:post_detail', post_id=post_id)  # Не автор поста получает редирект, автор идет дальше.

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)

        if form.is_valid():
            form.save()
            return redirect('posts:post_detail', post_id=post_id)
        return render(
            request,
            'posts/create_post.html',
            {'form': form, 'groups': groups, 'is_edit': is_edit, 'post': post},
        )

    form = PostForm(instance=post)  # При первом переходе обрабатываем GET-запрос - выдаем форму для заполнения.
    return render(
        request,
        'posts/create_post.html',
        {'form': form, 'groups': groups, 'is_edit': is_edit, 'post': post},
    )