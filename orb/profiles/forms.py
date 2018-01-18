# orb/profile/forms.py

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div
from crispy_forms.layout import HTML
from crispy_forms.layout import Layout
from crispy_forms.layout import Submit
from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.validators import validate_email
from django.utils.translation import ugettext_lazy as _

from orb.models import UserProfile


class LoginForm(forms.Form):
    username = forms.CharField(max_length=30,
                               error_messages={'required': _(
                                   u'Please enter a username.')},
                               label=_(u'Username'),
                               required=True,
                               )
    password = forms.CharField(widget=forms.PasswordInput,
                               error_messages={'required': _(
                                   u'Please enter a password.'), },
                               required=True,
                               label=_(u'Password'),
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
                Submit('submit', _(u'Login'),
                       css_class='btn btn-default'),
                HTML(u'<a class="btn btn-default" href="%s">%s</a>' % (reverse('profile_reset'),_(u'Forgotten password?'))),
                css_class='col-lg-offset-2 col-lg-4',
            ),
        )

    def clean(self):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        user = authenticate(username=username, password=password)
        if user is None or not user.is_active:
            raise forms.ValidationError(
                _(u"Invalid username or password. Please try again."))
        return cleaned_data


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True, label=_(u'Email'))
    password = forms.CharField(widget=forms.PasswordInput,
                               error_messages={'required': _(u'Please enter a password.'),
                                               'min_length': _(u'Your password should be at least 6 characters long.')},
                               min_length=6,
                               required=True,
                               label=_(u'Password'))
    password_again = forms.CharField(widget=forms.PasswordInput,
                                     min_length=6,
                                     error_messages={'required': _(u'Please enter your password again.'),
                                                     'min_length': _(u'Your password again should be at least 6 characters long.')},
                                     required=True,
                                     label=_(u'Password again'))
    first_name = forms.CharField(max_length=100,
                                 error_messages={'required': _(u'Please enter your first name.'),
                                                 'min_length': _(u'Your first name should be at least 2 characters long.')},
                                 min_length=2,
                                 required=True,
                                 label=_(u'First name'))
    last_name = forms.CharField(max_length=100,
                                error_messages={'required': _(u'Please enter your last name.'),
                                                'min_length': _(u'Your last name should be at least 2 characters long.')},
                                min_length=2,
                                required=True,
                                label=_(u'Last name'))
    role = forms.ChoiceField(widget=forms.Select,
                                required=False,
                                help_text=_(u'Please select from the options above, or enter in the field below:'),
                                label=_(u'Role'))
    role_other = forms.CharField(label='&nbsp;',
                                 max_length=100,
                                 required=False)
    organisation = forms.CharField(max_length=100,
                                   required=True,
                                   label=_(u'Organisation'))
    age_range = forms.ChoiceField(
                                    required=False,
                                    error_messages={'required': _(u'Please select an age range')},
                                    label=_(u'Age Range'))
    gender = forms.ChoiceField(
                                required=False,
                                error_messages={'required': _(u'Please select a gender')},
                                label=_(u'Gender'))

    terms = forms.BooleanField(
        label=_(u"Please tick the box to confirm that you have read the <a href='/terms/' target='_blank' class='prominent'>terms</a> about registering with ORB"),
        required=True,
        error_messages={'required': _(u'Please tick the box to confirm that you have read the terms')})
    mailing = forms.BooleanField(
        label=_(u"Subscribe to mPowering update emails"),
        required=False)
    survey = forms.BooleanField(
        label=_("I allow mPowering to ask me to participate in surveys about my usage of ORB resources"),
        required=False,
        initial=True,
    )

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
            'organisation',
            'role',
            'role_other',
            'age_range',
            'gender',
            'mailing',
            'survey',
            'terms',
            Div(
                Submit('submit', _(u'Register'),
                       css_class='btn btn-default'),
                css_class='col-lg-offset-2 col-lg-4',
            ),
        )

    def save_profile(self):
        """Creates User and UserProfile pair from form and returns UserProfile"""
        email = self.cleaned_data.get("email")
        password = self.cleaned_data.get("password")
        first_name = self.cleaned_data.get("first_name")
        last_name = self.cleaned_data.get("last_name")
        user = User.objects.create_user(email, email, password)
        user.first_name = first_name
        user.last_name = last_name
        user.save()
        return UserProfile.objects.create(
            user=user,
            mailing=self.cleaned_data['mailing'],
            survey=self.cleaned_data['survey'],
        )

    def authenticate_user(self):
        """Returns an authenticated user given email and password in form

        This must be run after the user has been created
        """
        return authenticate(username=self.cleaned_data['email'], password=self.cleaned_data['password'])

    def clean(self):
        cleaned_data = self.cleaned_data
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")

        if User.objects.filter(username__iexact=email).exists():
            raise forms.ValidationError(_(u"Username has already been registered, please select another."))

        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError(_(u"Email has already been registered"))

        if password and password_again and (password != password_again):
            raise forms.ValidationError(_(u"Passwords do not match."))

        # Check either a role is selected or other is entered
        role = cleaned_data.get("role")
        role_other = cleaned_data.get("role_other")
        if role == '0' and role_other == '':
            raise forms.ValidationError(_(u"Please select or enter a role"))

        if cleaned_data.get("age_range") == '0':
            raise forms.ValidationError(_(u"Please select an age range"))

        if cleaned_data.get("gender") == '0':
            raise forms.ValidationError(_(u"Please select a gender"))

        return cleaned_data


class ResetForm(forms.Form):
    username = forms.CharField(label=_(u'Username or email'),
                               max_length=100,
                               error_messages={'invalid': _(
                                   u'Please enter a username or email address.')},
                               required=True)

    def __init__(self, *args, **kwargs):
        super(ResetForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('profile_reset')
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-4'
        self.helper.layout = Layout(
            'username',
            Div(
                Submit('submit', _(u'Reset password'),
                       css_class='btn btn-default'),
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
                raise forms.ValidationError(_(u"Username/email not found"))
        return cleaned_data


class ProfileForm(forms.Form):
    api_key = forms.CharField(label=_(u'API key'),
                              widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                              required=False,
                              help_text=_(u'You cannot edit your API Key.'))
    username = forms.CharField(label=_(u'Username'),
                               widget=forms.TextInput(attrs={'readonly': 'readonly'}),
                               required=False, help_text=_(u'You cannot edit your username.'))
    email = forms.CharField(label=_(u'Email'),
                            validators=[validate_email],
                            error_messages={'invalid': _(
                                u'Please enter a valid e-mail address.')},
                            required=True)
    password = forms.CharField(label=_(u'Password'),
                               widget=forms.PasswordInput,
                               required=False,
                               min_length=6,
                               error_messages={'min_length': _(u'Your new password should be at least 6 characters long')},)
    password_again = forms.CharField(label=_(u'Password again'),
                                     widget=forms.PasswordInput,
                                     required=False,
                                     min_length=6)
    first_name = forms.CharField(label=_(u'First name'),
                                 max_length=100,
                                 min_length=2,
                                 required=True)
    last_name = forms.CharField(label=_(u'Last name'),
                                max_length=100,
                                min_length=2,
                                required=True)
    photo = forms.ImageField(label=_(u'Photo'),
                                required=False,
                                error_messages={},)
    role = forms.ChoiceField(label=_(u'Role'),
                                widget=forms.Select,
                                required=False,
                                help_text=_(u'Please select from the options above, or enter in the field below:'), )
    role_other = forms.CharField(label='&nbsp;',
                                 max_length=100,
                                 required=False)
    organisation = forms.CharField(label=_(u'Organisation'),
                                    max_length=100,
                                    required=False)
    age_range = forms.ChoiceField(label=_(u'Age range'),
                                widget=forms.Select,
                                required=True,
                                error_messages={'required': _(u'Please select an age range')},)
    gender = forms.ChoiceField(label=_(u'Gender'),
                                widget=forms.Select,
                                required=True,
                                error_messages={'required': _(u'Please select a gender')},)
    mailing = forms.BooleanField(
                                label=_(u"Please tick the box to subscribe to mPowering update emails"),
                                required=False)

    website = forms.CharField(label=_(u'Website'),
                              max_length=100,
                              required=False)
    twitter = forms.CharField(label=_(u'Twitter'),
                              max_length=100,
                              required=False)
    about = forms.CharField(label=_(u'About'),
                            widget=forms.Textarea,
                            required=False)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_action = reverse('my_profile_edit')
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
                HTML(u'<h3>%s</h3>' % _(u'Change password')),
            ),
            'password',
            'password_again',
            Div(
                HTML(u'<h3>%s</h3>' % _(u'API Key')),
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
        num_rows = User.objects.exclude(
            username__exact=username).filter(email=email).count()
        if num_rows != 0:
            raise forms.ValidationError(_(u"Email address already in use"))

        # if password entered then check they are the same
        password = cleaned_data.get("password")
        password_again = cleaned_data.get("password_again")
        if password and password_again:
            if password != password_again:
                raise forms.ValidationError(_(u"Passwords do not match."))

        return cleaned_data
