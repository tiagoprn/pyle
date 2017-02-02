from django.contrib.auth.models import User
from rest_framework import serializers

from .models import Tag, Link


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    tags = serializers.HyperlinkedRelatedField(many=True,
                                               read_only=True,
                                               view_name='tag-detail')

    class Meta:
        model = Link
        fields = (
            'owner',
            'url',
            'uri',
            'name',
            'created',
            'notes',
            'content',
            'content_last_updated_at',
            'tags'
        )


class LinkShortenedSerializer(serializers.HyperlinkedModelSerializer):
    # This is used to serialize the links with less information than "LinkSerializer".
    class Meta:
        model = Link
        fields = (
            'url',
            'uri',
            'name',
        )


class TagShortenedSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'url',
            'name',
        )


class TagSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    links = serializers.HyperlinkedRelatedField(many=True, read_only=True,
                                                view_name='link-detail')  # Link.tags related_name=links

    class Meta:
        model = Tag
        fields = (
            'owner',
            'url',
            'name',
            'created',
            'links',
        )


class UserSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagShortenedSerializer(many=True, read_only=True)  # Tag.owner related_name=tags
    links = LinkShortenedSerializer(many=True, read_only=True)  # Link.owner related_name=links

    class Meta:
        model = User
        fields = (
            'url',
            'pk',
            'username',
            'tags',
            'links',
        )
