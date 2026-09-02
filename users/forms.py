from django import forms
from django.contrib.auth.models import User

class CustomSignupForm(forms.ModelForm):
    # 1. Normal Fields
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        error_messages={'required': "First name is required."}
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        error_messages={'required': "Last name is required."}
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        error_messages={
            'required': "Email ID is required!",
            'invalid': "Please enter a valid email ID."
        }
    )
    
    # 2. Password Fields (PasswordInput widget se characters hide ho jayenge)
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(),
        error_messages={'required': "Password is required."}
    )
    confirm_password = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(),
        error_messages={'required': "Confirm password is required."}
    )

    class Meta:
        model = User
        # fields array me password define karne ki zaroorat nahi, wo upar explicitly declared hain
        fields = ("username", "first_name", "last_name", "email")
        error_messages = {
            'username': {
                'unique': "Yeh username is already taken.",
                'required': "Username is required.",
            }
        }

    # 3. Custom Validations
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Yeh email ID pehle se registered hai.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and len(username) < 5:
            raise forms.ValidationError("Username kam se kam 5 characters ka hona chahiye!")
        return username

    # Yeh function poore form ke submit hone par ek sath check karta hai
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check karein ki dono passwords aapas me match ho rahe hain ya nahi
        if password and confirm_password and password != confirm_password:
            # add_error se error specifically 'confirm_password' field par dikhega
            self.add_error('confirm_password', "Dono passwords aapas me match nahi kar rahe hain!")
        
        return cleaned_data

    # 4. Save & Hash Logic
    def save(self, commit=True):
        # Model object banayein par abhi database me save na karein
        user = super().save(commit=False)
        
        # User ke password ko securely hash (encrypt) karein
        user.set_password(self.cleaned_data["password"])
        
        if commit:
            user.save()
        return user

class LoginForm(forms.Form):
    email = forms.EmailField(
        label="Email Address",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'})
    )    