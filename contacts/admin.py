from django.contrib import admin
from .models import Contact, ContactStatusChoices


admin.site.register(ContactStatusChoices)
admin.site.register(Contact)
