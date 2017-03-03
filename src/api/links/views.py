import json

from django.contrib.auth.models import User
from django.http import JsonResponse

from rest_framework.views import exception_handler

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.reverse import reverse

from .models import Link, Tag
from .permissions import IsOwner
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
    queryset = Tag.objects.all()  # Although we bring all here, below on "get_queryset" we filter by the current user
    serializer_class = TagSerializer
    name = 'tag-list'
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner
    )
    filter_fields = ('name', 'created', 'owner')
    search_fields = ('name', 'created', 'owner')
    ordering_fields = ('-created',)

    def get_queryset(self):
        queryset = super(TagList, self).get_queryset()
        if self.request.user:
            return queryset.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Pass an additional owner field to the create method,
        # to set the owner to the user received in the request
        serializer.save(owner=self.request.user)


class TagDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    name = 'tag-detail'
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner
    )


class LinkList(generics.ListCreateAPIView):
    queryset = Link.objects.all()  # Although we bring all here, below on "get_queryset" we filter by the current user
    serializer_class = LinkSerializer
    name = 'link-list'
    permission_classes = (
        permissions.IsAuthenticated,
        IsOwner
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
        permissions.IsAuthenticated,
        IsOwner
    )


class ApiRoot(generics.GenericAPIView):
    name = 'api-root'

    def get(self, request, *args, **kwargs):
        return Response({
            'links': reverse(LinkList.name, request=request),
            'tags': reverse(TagList.name, request=request),
            'users': reverse(UserList.name, request=request)
        })


def api_500_handler(exception, context):
    response = exception_handler(exception, context)
    try:
        detail = response.data['detail']
    except Exception:
        detail = 'EXCEPTION: {}'.format(str(exception))

    payload = {'error': detail}
    if response:
        payload['status_code'] = response.status_code

    return Response(
        payload,
        content_type="application/json",
        status=status.HTTP_500_INTERNAL_SERVER_ERROR
    )


def api_404_handler(request):
    payload = {'error': 'resource not found, check its path.',
               'status_code': 404}

    return JsonResponse(payload, status=404)
