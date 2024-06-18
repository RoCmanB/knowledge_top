from django import forms
from django_summernote.widgets import SummernoteWidget

from .models import Comment, Post


class PostForm(forms.ModelForm):
    text = forms.CharField(widget=SummernoteWidget())

    class Meta:
        model = Post
        fields = ('title', 'text', 'group', 'image',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
