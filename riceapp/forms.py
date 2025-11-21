# Import necessary Django form modules and models
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import ClassificationResult

# Custom user registration form that extends Django's built-in UserCreationForm
class CustomUserCreationForm(UserCreationForm):
    # Add an email field that is required
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control','placeholder': 'Enter your email'}))
    
    # Meta class defines which model and fields to use
    class Meta:
        model = User  # Uses Django's built-in User model
        fields = ['username', 'email', 'password1', 'password2']  # Fields to include in form
        
    # Custom initialization method to apply styling to all form fields
    def __init__(self, *args, **kwargs):
        # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)
        # Loop through all fields in the form
        for field in self.fields:
            # Update each field's widget attributes to add CSS classes and placeholders
            self.fields[field].widget.attrs.update({
                'class': 'form-control',  # Bootstrap CSS class for styling
                'placeholder': f'Enter your {field}'  # Dynamic placeholder text
            })

# Custom authentication form that extends Django's built-in AuthenticationForm
class CustomAuthenticationForm(AuthenticationForm):
    # Custom initialization method to apply styling to all form fields
    def __init__(self, *args, **kwargs):
        # Call the parent class's __init__ method
        super().__init__(*args, **kwargs)
        # Loop through all fields in the form (username and password)
        for field in self.fields:
            # Update each field's widget attributes to add CSS classes and placeholders
            self.fields[field].widget.attrs.update({'class': 'form-control',  # Bootstrap CSS class for styling
                'placeholder': f'Enter your {field}'  # Dynamic placeholder text
            })

# Form for uploading images
class ImageUploadForm(forms.Form):
    # Image field that accepts image files
    image = forms.ImageField(
        # Custom widget to style the file input
        widget=forms.FileInput(attrs={
            'class': 'form-control',  # Bootstrap CSS class
            'accept': 'image/*'  # HTML attribute to only accept image files
        })
    )