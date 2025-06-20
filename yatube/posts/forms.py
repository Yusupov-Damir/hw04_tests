from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group')

    def clean_text(self):
        data = self.cleaned_data['text']

        #if data == '': # Эта проверка не нужна, так как дублирует вшитую в дженерик класс валидацию.
            #raise forms.ValidationError('Напишите пост')
        #return data
        if len(data) < 2:
            raise forms.ValidationError('Пост должен содеражать более 2-ух символов')
        return data
