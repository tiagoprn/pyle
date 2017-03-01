from rest_framework import permissions


# Create a new permission here: "IsOwner"

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:  # GET, HEAD or OPTIONS always allowed access
            return True
        else:
            return obj.owner == request.user  # allowed access only on this condition, otherwise denied


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user  # the permission shall be granted only on this condition
