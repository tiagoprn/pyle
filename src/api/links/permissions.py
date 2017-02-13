from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD or OPTIONS
            return True
        else:
            return obj.owner == request.user  # the permission shall be granted only on this condition
