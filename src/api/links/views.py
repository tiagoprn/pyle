from django.contrib.auth.models import User

from django_filters import NumberFilter, DateTimeFilter, AllValuesFilter

from rest_framework import filters, generics, permissions
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.throttling import ScopedRateThrottle

from .models import Link, Tag
from .permissions import IsOwnerOrReadOnly
from .serializers import (LinkSerializer,
                          TagSerializer,
                          UserSerializer)


'''
For each model, there are 2 classes, that inherit from:
    . ListCreateAPIView: GET / POST on a collection (list)
    . RetrieveUpdateDestroyAPIView: GET / PUT / PATCH / DELETE on a single object (detail)
The exception is the user model, that inherits from:
    . ListAPIView: Implements the GET method for a collection
    . RetrieveAPIView: Implements the GET method for an instance
In the end, there is the ApiRoot class, that is the entry endpoint for all the other models.
'''


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = 'user-list'


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    name = 'user-detail'


class TagList(generics.ListCreateAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    name = 'tag-list'
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )
    filter_fields = ('name', 'created', 'owner')
    search_fields = ('name', 'created', 'owner')
    ordering_fields = ('-created',)

    def perform_create(self, serializer):
        # Pass an additional owner field to the create method,
        # to set the owner to the user received in the request
        serializer.save(owner=self.request.user)


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    name = 'tag-detail'
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )


class LinkList(generics.ListCreateAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    name = 'link-list'
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )
    filter_fields = ('name', 'created', 'owner', 'uri')
    search_fields = ('name', 'created', 'owner', 'uri')
    ordering_fields = ('-created',)

    def perform_create(self, serializer):
        # Pass an additional owner field to the create method,
        # to set the owner to the user received in the request
        serializer.save(owner=self.request.user)


class LinkDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Link.objects.all()
    serializer_class = LinkSerializer
    name = 'link-detail'
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
    )


class ApiRoot(generics.GenericAPIView):
    name = 'api-root'

    def get(self, request, *args, **kwargs):
        return Response({
            'links': reverse(LinkList.name, request=request),
            'tags': reverse(TagList.name, request=request),
            'users': reverse(UserList.name, request=request)
        })
