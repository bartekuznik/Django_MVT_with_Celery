from django import forms
from .models import Contact

class ContactForm(forms.ModelForm):
    """
    Extended version for create and update froms. This Contact 
    Form contain more validation conditionals than default version.
        
    Methods:
        clean_first_name(): Checks if first_name in form doesen't contain 
                            numbers or whitespaces.
        clean_last_name(): Checks if last_name in form doesen't contain 
                            numbers or whitespaces.
        clean_city(): Checks if last_name in form doesen't contain 
                      numbers 
        clean_phone_number(): Checks if phone_number in form doesen't contain 
                              letters and have length 9
    """
    class Meta:
        model = Contact
        fields = [
                'first_name',
                'last_name',
                'phone_number',
                'email',
                'city',
                'status',
                'shared_with']
        widgets ={
            'first_name': forms.TextInput(attrs={
                'required': 'required',
            }),
            'last_name': forms.TextInput(attrs={
                'required': 'required',
            }),
            'city': forms.TextInput(attrs={
                'required': 'required',
            }),
            'phone_number': forms.TextInput(attrs={
                'required': 'required',
            }),
        }

    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if any(char.isdigit() for char in first_name):
            raise forms.ValidationError("The name cannot contain numbers.")
        if " " in first_name:
            raise forms.ValidationError("The name cannot contain spaces.")
        return first_name.capitalize()
    
    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if any(char.isdigit() for char in last_name):
            raise forms.ValidationError("The last name cannot contain numbers.")
        if " " in last_name:
            raise forms.ValidationError("The last name cannot contain spaces.")
        return last_name.capitalize()
    
    def clean_city(self):
        city = self.cleaned_data['city']
        if any(char.isdigit() for char in city):
            raise forms.ValidationError("The city cannot contain numbers.")
        return city
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if not phone_number.isnumeric():
            raise forms.ValidationError("The phone number cannot contain letters.")
        elif len(phone_number) != 9:
            raise forms.ValidationError("The phone number should have 9 numbers.")
        return phone_number

class ContactImportForm(forms.Form):
    file = forms.FileField(label="Choose CSV file")
    