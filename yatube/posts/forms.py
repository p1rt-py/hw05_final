from django import forms

from .models import Comment, Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст нового поста',
                  'group': 'Группа, к которой относится пост'
                  }

        help_text = {
            'text': 'Текст поста',
            'group': 'Группа поста'
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
