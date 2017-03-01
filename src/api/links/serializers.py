from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework.fields import CurrentUserDefault

from .models import Tag, Link, LinkTag


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


class LinkSerializer(serializers.HyperlinkedModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')
    # http://stackoverflow.com/questions/28706072/drf-3-creating-many-to-many-update-create-serializer-with-though-table
    tags = TagShortenedSerializer(many=True, required=False)

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

    def _get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def create(self, validated_data):
        tags_data = validated_data.pop('tags')
        link = Link.objects.create(**validated_data)
        for tag in tags_data:
            tag_instance, created = Tag.objects.get_or_create(name=tag['name'],
                                                              owner=self._get_current_user())
            LinkTag.objects.create(link=link, tag=tag_instance)
        return link

    def update(self, instance, validated_data):
        try:
            tags_data = validated_data.pop('tags')
        except:
            tags_data = {}
        for item in validated_data:
            if Link._meta.get_field(item):
                setattr(instance, item, validated_data[item])
        LinkTag.objects.filter(link=instance).delete()
        for tag in tags_data:
            tag_instance, created = Tag.objects.get_or_create(name=tag['name'],
                                                              owner=self._get_current_user())
            LinkTag.objects.create(link=instance, tag=tag_instance)
        instance.save()
        return instance


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

    def _get_current_user(self):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        return user

    def create(self, validated_data):
        # If the user tries to create a tag which already exists,
        # I will just return the existing one.
        instance = Tag.objects.filter(name=validated_data['name'],
                                      owner=self._get_current_user()).first()
        if instance:
            tag = instance
        else:
            tag = Tag.objects.create(**validated_data)
        return tag



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
