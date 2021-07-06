from rest_framework import permissions


class FixPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.user.is_authenticated:
            if request.method == 'GET':
                return True
            # if view.action == 'retrieve':
            #     return request.user.has_perms('fix_an_appointment')
        return True

    def has_object_permission(self, request, view, obj):
        print(obj)
        return True
