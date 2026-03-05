from django.shortcuts import redirect, render
from django.db import transaction
from contacts.tasks import get_geo_data, get_weather_data
from .models import Contact, ContactStatusChoices
from .forms import ContactForm, ContactImportForm
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
import tablib
from django.core.cache import cache
from django.contrib.auth.decorators import login_required

class ContactListView(LoginRequiredMixin, ListView):
    """
    View for displaying a paginated list of contacts.
    
    Methods:
        get_queryset(): Retrieves contacts owned by or shared with the current user. 
                        Includes logic for dynamic ordering and populates each 
                        contact with cached weather data. If weather data is 
                        missing, it triggers an asynchronous Celery task to 
                        fetch it.
    """
    model = Contact
    template_name = 'contacts/contact_list.html'
    context_object_name = 'contacts'
    paginate_by = 6

    def get_queryset(self):
        queryset = Contact.objects.filter(
            Q(owner = self.request.user) | Q(shared_with=self.request.user)).distinct().select_related('status')
        
        order_by = self.request.GET.get('order', 'last_name')
        allowed_orders = ['last_name','-last_name','created_at','-created_at']

        if order_by not in allowed_orders:
            queryset
        else:
            queryset = queryset.order_by(order_by)

        for contact in queryset:
            cache_key = f'weather_data_contact_{contact.id}'
            cached_weather = cache.get(cache_key)
            if cached_weather:
                contact.weather = cached_weather

            else:
                contact.weather ={
                    'temperature': "N/A",
                    'humidity': 'N/A',
                    'windspeed': 'N/A',
                    'is_day': 'N/A',
                    'rain': 'N/A',
                    'cloud_cover': 'N/A',
                    }
                if contact.latitude is not None and contact.longitude is not None:
                    get_weather_data.delay(cache_key, contact.latitude, contact.longitude)
        
        return queryset

        

class ContactDetailView(LoginRequiredMixin, DetailView):
    """
    View for displaying details of a specific contact.

    Methods:
        get_queryset(): Restricts access to ensure that only the owner 
                        or users with whom the contact is shared can 
                        view the details.
    """
    model = Contact
    template_name = 'contacts/contact_detail.html'

    def get_queryset(self):
        queryset = Contact.objects.filter(
            Q(owner = self.request.user) | Q(shared_with=self.request.user)).distinct().select_related('status')
        return queryset
    
class ContactCreateView(LoginRequiredMixin, CreateView):
    """
    View for creating a new contact.
        
    Methods:
        form_valid(): Automatically assigns the current user as the contact owner. 
                      Triggers an asynchronous background task to fetch geographical 
                      data (latitude/longitude) after the database transaction is committed. 
                      Data ich fetched form  'nominatim' API.

    """

    model = Contact
    form_class = ContactForm
    template_name = 'contacts/create_contact.html'
    success_url = reverse_lazy('contact_list')

    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        contact = self.object
        transaction.on_commit(lambda i_id=contact.id, i_city=contact.city: get_geo_data.delay(i_id, i_city))        
        return response
    
class ContactUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for updating a contact.
        
    Methods:
        form_valid(): Checks if the city field has changed. If a new city is 
                      provided, it triggers an asynchronous Celery task to 
                      refresh geographical data (latitude/longitude) after 
                      the database transaction is committed.

    """
    model = Contact
    form_class = ContactForm
    template_name = 'contacts/edit_contact.html'
    success_url = reverse_lazy('contact_list')
    
    def form_valid(self, form):
        old_city = self.get_object().city
        new_city = form.cleaned_data.get('city')
        response = super().form_valid(form)

        if old_city != new_city:
            
            cache_key = f'weather_data_contact_{contact.id}'
            cache.delete(cache_key)

            contact = self.object
            transaction.on_commit(lambda i_id=contact.id, i_city=contact.city: get_geo_data.delay(i_id, i_city)) 

        return response
    
class ContactDeleteView(LoginRequiredMixin, DeleteView):
    """
    View for deleting a contact.
    """
    model = Contact
    template_name = 'contacts/delete_contact.html'
    success_url = reverse_lazy('contact_list')

@login_required
def import_contacts(request):
    """
    View for importing contacts from a CSV file.
    
    Processing Steps:
        1. Reads and decodes the uploaded CSV file using tablib.
        2. Get contact status choices into a dictionary for efficient checks integrity.
        3. Iterates through the dataset, creating Contact objects.
        4. Triggers background Celery tasks for geolocation after each 
           successful database commit.
        5. Collects errors for rows that fail validation or creation.
    """

    form = ContactImportForm(request.POST, request.FILES)
    errors = []

    if request.method == 'POST' and request.FILES.get('file'):
        
        csv_file = request.FILES['file']
        data = csv_file.read().decode('utf-8')
        dataset = tablib.Dataset().load(data, format='csv')

        contact_choices = {c.status: c for c in ContactStatusChoices.objects.all()} 
        
        for row in dataset.dict:
            row_contact_choices = row.get('status')
            row_contact_choices_object = contact_choices.get(row_contact_choices)     
            
            try:
                with transaction.atomic():
                    contact = Contact.objects.create(
                        first_name = row.get('first_name'),
                        last_name = row.get('last_name'),
                        phone_number = row.get('phone_number'),
                        email = row.get('email'),
                        city = row.get('city'),
                        status = row_contact_choices_object,
                        owner = request.user
                    )

                    transaction.on_commit(lambda c_id=contact.id, c_city=contact.city: get_geo_data.delay(c_id, c_city)) 
            
            except Exception as e:
                errors.append(f"Unexpected import error for {row.get('email')}. Please check the format and existing contacts")
    
    return render(request, 'contacts/contact_import.html',{"form":form, "errors": errors})

@login_required
def unsubscribe_contact(request, id):
    """
    Removes the current user from the contact's shared access list.
    
    """
    if request.method == 'POST':
        contact = Contact.objects.get(id = id)
        contact.shared_with.remove(request.user)
    return redirect(reverse_lazy('contact_list'))

def home(request):
    return render(request, 'contacts/home.html')