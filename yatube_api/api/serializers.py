from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from rest_framework.validators import UniqueTogetherValidator

from django.contrib.auth import get_user_model

from posts.models import Comment, Post, Group, Follow

User = get_user_model()


class PostSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Post


class CommentSerializer(serializers.ModelSerializer):

    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )
    post = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        fields = '__all__'
        model = Comment


class GroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    user = SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all(),
        default=serializers.CurrentUserDefault()
    )
    following = serializers.SlugRelatedField(
        slug_field='username',
        queryset=User.objects.all()
    )

    class Meta:
        fields = ('user', 'following')
        model = Follow
        validators = (
            UniqueTogetherValidator(
                fields=('user', 'following'),
                queryset=Follow.objects.all(),
                message=('Вы уже оформили подписку!')
            ),
        )

    def validate(self, data):
        if data['user'] == data['following']:
            raise serializers.ValidationError(
                'Подписку на себя оформить невозможно!'
            )
        return data

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
