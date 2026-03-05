from django.urls import path, include
from .views import ContactListView, ContactDetailView, ContactCreateView, ContactDeleteView, ContactUpdateView, import_contacts, unsubscribe_contact, home
from .api_views import ContactGetViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()

router.register(r'contacts', ContactGetViewSet, basename='contact')

urlpatterns = [
    #API views
    path('api/', include(router.urls)),

    #MVT views
    path('', home, name='home'),
    path('contacts', ContactListView.as_view(),name='contact_list'),
    path('contacts/<pk>', ContactDetailView.as_view(),name='contact_detail'),
    path('contact/add/',ContactCreateView.as_view(), name='contact_create'),
    path('contact/import/', import_contacts , name='contact_import'),
    path('contact/<int:pk>/update/', ContactUpdateView.as_view(),name='contact_update'),
    path('contact/<int:pk>/delete/', ContactDeleteView.as_view(),name='contact_delete'),
    path('contact/<int:id>/unsubscribe/', unsubscribe_contact,name='contact_unsubscribe'),
]