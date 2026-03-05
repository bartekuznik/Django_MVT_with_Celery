from django.db import models
from django.contrib.auth.models import User

class ContactStatusChoices(models.Model):
    status = models.CharField(primary_key=True, max_length=300, unique=True)

    def __str__(self):
        return self.status

class Contact(models.Model):
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='my_contacts'
    )
    shared_with = models.ManyToManyField(
        User, 
        related_name='shared_with_me', 
        blank=True
    )
    first_name = models.CharField(max_length=300)
    last_name = models.CharField(max_length=300)
    phone_number = models.CharField(max_length=9)
    email = models.EmailField()
    city = models.CharField(max_length=300)
    status = models.ForeignKey(ContactStatusChoices, related_name='contacts', null=True,on_delete=models.SET_NULL)
    created_at = models.DateTimeField(auto_now_add=True)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['owner', 'email'],
                name='unique_contact_email_per_owner',
                violation_error_message='You already have contact with the provided email'
            ),
            models.UniqueConstraint(
                fields=['owner', 'phone_number'],
                name='unique_contact_phone_number_per_owner',
                violation_error_message='You already have contact with the provided phone number'
            ),
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"