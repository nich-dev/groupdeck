from rest_framework import permissions
from rest_framework.authentication import SessionAuthentication 

class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return  # To not perform the csrf check previously happening    

class IsUserOrAdmin(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.user.is_staff or request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj == request.user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj.user_created == request.user
    
class IsUserOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        # Write permissions are only allowed to the owner of the snippet.
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - owner may GET, PUT, POST, DELETE
     - nobody else can access
    """

    def has_object_permission(self, request, view, obj):
        # permissions are only allowed to the owner of the snippet.
        return obj.user_created == request.user


class ReadOnly(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - anyone can may GET,
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True

        return False

class ReadOnlyOrCreate(permissions.BasePermission):
    """
    Handles permissions for users.  The basic rules are

     - anyone can may GET, HEAD, OPTIONS, or CREATE
     - No one may PUT, DELETE unless staff
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.user.is_staff:
            return True
        elif request.method in permissions.SAFE_METHODS or request.method == 'POST':
            return True

        return False

class IsPlayer(permissions.BasePermission):
    """
    Only allow players of a gameroom, or contains secret key
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        if type(obj).__name__ == 'Card':
            return True
        key = request.query_params.get('key', None)
        if key and request.user.is_anonymous():            
            return (key and key == obj.secret) and obj.allow_guests
        elif key and key == obj.secret and request.user not in obj.players.all():
            obj.players.add(request.user) 
            return True
        elif request.user.is_anonymous():
            return False
        return request.user == obj.user_created or request.user in obj.players.all()

class CanDraw(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        if type(obj).__name__ == 'Card':
            return True
        if request.user.is_anonymous():
            key = request.query_params.get('key', None)
            return (key and key == obj.secret) and obj.allow_guests and obj.open_draw
        return request.user == obj.user_created or (request.user in obj.players.all() and obj.open_draw)
    
class DisableCSRF(object):
    def process_request(self, request):
            setattr(request, '_dont_enforce_csrf_checks', True)
