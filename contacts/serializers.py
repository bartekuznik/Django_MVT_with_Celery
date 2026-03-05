from rest_framework import serializers
from .models import Contact

class ContactModelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contact model.
    """
    class Meta:
        model = Contact
        fields = [
            'id',
            'first_name',
            'last_name',
            'city',
            'status',
            'created_at'
        ]

class ContactAllFieldsModelSerializer(serializers.ModelSerializer):
    """
    Serializer for the Contact model.
    """
    class Meta:
        model = Contact
        fields = [
            'id',
            'first_name',
            'last_name',
            'shared_with',
            'phone_number',
            'email',
            'city',
            'status',
            'created_at',
        ]