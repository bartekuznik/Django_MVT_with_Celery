from .models import Contact
from rest_framework import viewsets
from .serializers import ContactModelSerializer, ContactAllFieldsModelSerializer
from django.db.models import Q
from .tasks import get_geo_data
from rest_framework import permissions
from django.db import transaction
from django.core.cache import cache

class ContactGetViewSet(viewsets.ModelViewSet):
    """
    API ViewSet for managing contacts.
        
    Methods:
        get_queryset(): Restricts results to contacts owned by or shared with the user.
        get_serializer_class(): Switches serializers based on the current action.
        perform_create(): Sets the owner and triggers background geolocation.
        perform_update(): Refreshes geolocation only if the city field has changed.
    """
    serializer_class = ContactAllFieldsModelSerializer    
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Contact.objects.filter(Q(owner = self.request.user) | Q(shared_with=self.request.user)).distinct().select_related('status')
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ContactModelSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return ContactAllFieldsModelSerializer 
        return super().get_serializer_class()
        
    def perform_create(self, serializer):
        instance = serializer.save(owner = self.request.user) 
        transaction.on_commit(lambda i_id=instance.id, i_city=instance.city: get_geo_data.delay(i_id, i_city))

    def perform_update(self, serializer):
        old_city = serializer.instance.city
        instance = serializer.save()
        new_city = instance.city

        if new_city and new_city != old_city:
            cache_key = f'weather_data_contact_{instance.id}'
            cache.delete(cache_key)
            transaction.on_commit(lambda i_id=instance.id, i_city=instance.city: get_geo_data.delay(i_id, i_city))
