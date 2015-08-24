# orb/profile/forms.py
import hashlib
import urllib

from django import forms
from django.conf import settings
from django.contrib.auth import (authenticate, login, views)
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Button, Layout, Fieldset, ButtonHolder, Submit, Div, HTML

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30, 
                               error_messages={'required': _(u'Please enter a username.')},
                               )
    password = forms.CharField(widget=forms.PasswordInput,
                                error_messages={'required': _(u'Please enter a password.'),},      
                                required=True,
                                help_text=_('Please note that your username and password are case-sensitive.'),)
    next = forms.CharField(widget=forms.HiddenInput())
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('profile_login')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
                                    'username',
                                    'password',
                                    'next',
                                Div(
                                   Submit('submit', _(u'Login'), css_class='btn btn-default'),
                                   HTML("""<a class="btn btn-default" href="{% url 'profile_reset' %}">"""+_(u'Forgotten password?') + """</a>"""),
                                   css_class='col-lg-offset-2 col-lg-4',
                                ),
        )
       
    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        
        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            raise forms.ValidationError( _(u"Invalid username or password. Please try again."))
        return cleaned_data
     
class RegisterForm(forms.Form):
    username = forms.CharField(max_length=30, 
                               min_length=4,
                               error_messages={'required': _(u'Please enter a username.')},)
    email = forms.CharField(validators=[validate_email],
                                error_messages={'invalid': _(u'Please enter a valid e-mail address.'),
                                                'required': _(u'Please enter your e-mail address.')},
                                required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                                error_messages={'required': _(u'Please enter a password.'),
                                                'min_length': _(u'Your password should be at least 6 characters long.')},
                                min_length=6,       
                                required=True)
    password_again = forms.CharField(widget=forms.PasswordInput,
                                    min_length=6,
                                    error_messages={'required': _(u'Please enter your password again.'),
                                                    'min_length': _(u'Your password again should be at least 6 characters long.')},
                                    required=True)
    first_name = forms.CharField(max_length=100,
                                    error_messages={'required': _(u'Please enter your first name.'),
                                                    'min_length': _(u'Your first name should be at least 2 characters long.')},
                                    min_length=2,
                                    required=True)
    last_name = forms.CharField(max_length=100,
                                error_messages={'required': _(u'Please enter your last name.'),
                                                'min_length': _(u'Your last name should be at least 2 characters long.')},
                                min_length=2,
                                required=True)
    role = forms.ChoiceField(
                        widget=forms.Select,
                        required=False,
                        help_text=_('Please select from the options above, or enter in the field below:'), )
    role_other = forms.CharField(label='&nbsp;',
                                 max_length=100,
                                 required=False)
    organisation = forms.CharField(max_length=100,required=False)
    age_range = forms.ChoiceField(
                        widget=forms.Select,
                        required=True,
                        error_messages={'required': _('Please select an age range')},)
    gender = forms.ChoiceField(
                        widget=forms.Select,
                        required=True,
                        error_messages={'required': _('Please select a gender')},)
     
    terms = forms.BooleanField(
                        label=_(u"Please tick the box to confirm that you have read the <a href='/terms/' target='_blank' class='prominent'>terms</a> about registering with ORB"),            
                        required=True,
                        error_messages={'required': _('Please tick the box to confirm that you have read the terms')})
    mailing = forms.BooleanField(
                        label=_(u"Subscribe to mPowering update emails"),            
                        required=False)
    

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('profile_register')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
                                    'username',
                                    'email',
                                    'password',
                                    'password_again',
                                    'first_name',
                                    'last_name',
                                    'role',
                                    'role_other',
                                    'organisation',
                                    'age_range',
                                    'gender',
                                    'mailing',
                                    'terms',
                                Div(
                                   Submit('submit', _(u'Register'), css_class='btn btn-default'),
                                   css_class='col-lg-offset-2 col-lg-4',
                                ),
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")
        username = cleaned_data.get("username")

        # check the username not already used
        num_rows = User.objects.filter(username=username).count()
        if num_rows != 0:
            raise forms.ValidationError( _(u"Username has already been registered, please select another."))
        
        # check the email address not already used
        num_rows = User.objects.filter(email=email).count()
        if num_rows != 0:
            raise forms.ValidationError( _(u"Email has already been registered"))

        # check the password are the same
        if password and password_again:
            if password != password_again:
                raise forms.ValidationError( _(u"Passwords do not match."))

        # Check either a role is selected or other is entered
        role = cleaned_data.get("role")
        role_other = cleaned_data.get("role_other")
        if role == '0' and role_other == '':
            raise forms.ValidationError( _(u"Please select or enter a role"))
        
        age_range = cleaned_data.get("age_range")
        if age_range == '0':
            raise forms.ValidationError( _(u"Please select an age range"))
        
        gender = cleaned_data.get("gender")
        if gender == '0':
            raise forms.ValidationError( _(u"Please select a gender"))
        
        # Always return the full collection of cleaned data.
        return cleaned_data

class ResetForm(forms.Form):
    username = forms.CharField(max_length=100,
        error_messages={'invalid': _(u'Please enter a username or email address.')},
        required=True)
    
    def __init__(self, *args, **kwargs):
        super(ResetForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Username or email"
        self.helper = FormHelper()
        self.helper.form_action = reverse('profile_reset')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
                                    'username',
                                Div(
                                   Submit('submit', _(u'Reset password'), css_class='btn btn-default'),
                                   css_class='col-lg-offset-2 col-lg-4',
                                ),
        )
    
    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
        try:
            user = User.objects.get(username__exact=username)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email__exact=username)
            except User.DoesNotExist:
                raise forms.ValidationError( _(u"Username/email not found"))
        return cleaned_data

class ProfileForm(forms.Form):
    api_key = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}),
                               required=False, help_text=_(u'You cannot edit your API Key.'))
    username = forms.CharField(widget = forms.TextInput(attrs={'readonly':'readonly'}),
                               required=False, help_text=_(u'You cannot edit your username.'))
    email = forms.CharField(validators=[validate_email],
                            error_messages={'invalid': _(u'Please enter a valid e-mail address.')},
                            required=True)
    password = forms.CharField(widget=forms.PasswordInput,
                               required=False,
                               min_length=6,
                               error_messages={'min_length': _(u'Your new password should be at least 6 characters long')},)
    password_again = forms.CharField(widget=forms.PasswordInput,
                                     required=False,
                                     min_length=6)
    first_name = forms.CharField(max_length=100,
                                 min_length=2,
                                 required=True)
    last_name = forms.CharField(max_length=100,
                                min_length=2,
                                required=True)
    photo = forms.ImageField(  
                required=False,
                error_messages={},)
    role = forms.ChoiceField(
                        widget=forms.Select,
                        required=False,
                        help_text=_('Please select from the options above, or enter in the field below:'), )
    role_other = forms.CharField(label='&nbsp;',
                                 max_length=100,
                                 required=False)
    organisation = forms.CharField(max_length=100,required=False)
    age_range = forms.ChoiceField(
                        widget=forms.Select,
                        required=True,
                        error_messages={'required': _('Please select an age range')},)
    gender = forms.ChoiceField(
                        widget=forms.Select,
                        required=True,
                        error_messages={'required': _('Please select a gender')},)
    mailing = forms.BooleanField(
                        label=_(u"Please tick the box to subscribe to mPowering update emails"),            
                        required=False)
    
    website = forms.CharField(max_length=100,
                                 required=False)
    twitter = forms.CharField(max_length=100,
                                 required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('profile_edit')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
                'photo',
                'username',
                'email',
                'first_name',
                'last_name',
                'role',
                'role_other',
                'organisation',
                'age_range',
                'gender',
                'about',
                'website',
                'twitter',
                'mailing',
                Div(
                    HTML("""<h3>"""+_(u'Change password') + """</h3>"""),
                    ),
                'password',
                'password_again',
                Div(
                    HTML("""<h3>"""+_(u'API Key') + """</h3>"""),
                    ),
                'api_key',
                Div(
                   Submit('submit', _(u'Save'), css_class='btn btn-default'),
                   css_class='col-lg-offset-2 col-lg-4',
                ),
            )

        
    def clean(self):
        cleaned_data = self.cleaned_data
        # check email not used by anyone else
        email = cleaned_data.get("email")
        username = cleaned_data.get("username")
        num_rows = User.objects.exclude(username__exact=username).filter(email=email).count()
        if num_rows != 0:
            raise forms.ValidationError( _(u"Email address already in use"))
        
        # if password entered then check they are the same
        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")
        if password and password_again:
            if password != password_again:
                raise forms.ValidationError( _(u"Passwords do not match."))
            
        return cleaned_data