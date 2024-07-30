from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(max_length=25)
    email = forms.EmailField()
    to = forms.EmailField()
    comments = forms.CharField(required=False,
                               widget=forms.Textarea)


class CommentForm(forms.ModelForm):
    """
    ModelForm автоматически генерирует поля,
    которых нет в форме
    """

    class Meta:
        # Поля какой модели использовать
        model = Comment
        # Отображаемые поля
        fields = ['name', 'email', 'body']


class SearchForm(forms.Form):
    query = forms.CharField()
