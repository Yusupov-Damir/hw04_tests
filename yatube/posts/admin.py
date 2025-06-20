from django.contrib import admin

from .models import Post
from  .models import Group


@admin.register(Post)  # Регистрирую и настраиваю отображение модели постов.
class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_editable = ('group',)
    search_fields = ('text',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


@admin.register(Group)  # Регистрирую мою модель групп.
class GroupAdmin(admin.ModelAdmin):
    pass


from django.contrib.auth.models import Group  # Импортирую встроенную модель групп, иначе ее не скрыть.
admin.site.unregister(Group)  # Принудительно отключаю отображение встроенной модели групп.