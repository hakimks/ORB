import logging

from crispy_forms.bootstrap import FieldWithButtons
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Div, Field, HTML, Layout, Row, Submit
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core.validators import URLValidator
from django.utils.functional import cached_property
from django.template.defaultfilters import filesizeformat
from django.utils.html import strip_tags
from django.utils.translation import ugettext_lazy as _

from orb.models import Resource, Tag

logger = logging.getLogger('orb')


class ResourceStep1Form(forms.Form):

    title = forms.CharField(
        label=_(u'Title'),
        required=True,
        error_messages={'required': _(u'Please enter a title')},)
    organisations = forms.CharField(
        label=_(u'Organisations'),
        help_text=_(u'Comma separated if entering more than one organisation'),
        required=True,
        error_messages={'required': _(u'Please enter at least one organisation')},)
    description = forms.CharField(
        label=_(u'Description'),
        widget=forms.Textarea,
        required=True,
        error_messages={'required': _(u'Please enter a description')},
        help_text=_(u'Please enter no more than %d words.' % settings.ORB_RESOURCE_DESCRIPTION_MAX_WORDS), )
    image = forms.ImageField(
        label=_(u'Image'),
        required=False,
        error_messages={},
        widget=forms.ClearableFileInput)
    health_topic = forms.MultipleChoiceField(
        label=_(u'Health domain'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': _(u'Please select at least one health domain')},)
    resource_type = forms.MultipleChoiceField(
        label=_(u'Resource type'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': _(u'Please select at least one resource type')},)
    audience = forms.MultipleChoiceField(
        label=_(u'Audience'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': _(u'Please select at least one audience')},)
    geography = forms.CharField(
        label=_(u'Geography'),
        required=True,
        help_text=_(u'The geographic area the resource is designed for, may be region e.g. ("Africa", "East Africa") or country (e.g. "Ethiopia", "Mali"). Comma separated if entering more than one geography'),
        error_messages={'required': _(u'Please enter at least one geographical area')},)
    languages = forms.CharField(
        label=_(u'Languages'),
        required=True,
        help_text=_(
            u'The languages the resource uses. Comma separated if entering more than one language'),
        error_messages={'required': _(u'Please enter at least one language')},)
    device = forms.MultipleChoiceField(
        label=_(u'Device'),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        error_messages={'required': _(u'Please select at least one device')},)
    license = forms.ChoiceField(
        label=_(u'License'),
        widget=forms.Select,
        required=True,
        error_messages={'required': _(u'Please select a license')},
        help_text=_(u"<a href='/cc-faq' target='_blank'>More information on Creative Commons licenses</a>"),)
    other_tags = forms.CharField(
        label=_(u'Other tags'),
        help_text=_(
            u'Please enter any other relevant tags for this resource, comma separated if entering more than one tag'),
        required=False,
    )
    terms = forms.BooleanField(
        label=_(u"Please tick the box to confirm that you have read the <a href='/resource/guidelines/' target='_blank' class='prominent'>guidelines and criteria</a> for submitting resources to ORB"),
        required=True,
        error_messages={'required': _(u'Please tick the box to confirm that you have read the guidelines for submitting resources to ORB')})
    study_time_number = forms.IntegerField(
        required=False,
        label="",)
    study_time_unit = forms.CharField(
        label="",
        widget=forms.Select(choices=Resource.STUDY_TIME_UNITS),
        required=False,)
    attribution = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 2,
                                     'style': 'resize:none;'}),
        required=False,
        help_text=_(
            u'Please enter any specific text you would like to be used for the attribution for this resource'),
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.user = kwargs.pop('user', None)
        if self.request and not self.user:
            self.user = self.request.user

        super(ResourceStep1Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.attrs = {'novalidate': True}
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'title',
            'organisations',
            'description',
            'image',
            Row(HTML('<hr>')),
            'health_topic',
            Row(HTML('<hr>')),
            'resource_type',
            Row(HTML('<hr>')),
            Div(
                Div(
                    HTML(
                        u"<label class='control-label' style='float:right; padding-right:10px;'>{0}</label>".format(
                            _(u"Study Time")
                        )),
                    css_class='col-lg-2 '
                ),
                Div(
                    Field('study_time_number'),
                    css_class='col-lg-2'
                ),
                Div(
                    Field('study_time_unit'),
                    css_class='col-lg-2'
                ),
                css_class='row',
            ),
            Row(HTML('<hr>')),
            'audience',
            Row(HTML('<hr>')),
            'geography',
            Row(HTML('<hr>')),
            'languages',
            Row(HTML('<hr>')),
            'device',
            Row(HTML('<hr>')),
            'license',
            'attribution',
            Row(HTML('<hr>')),
            'other_tags',
            Row(HTML('<hr>')),
            'terms',
            Row(HTML('<hr>')),
            Div(
                Submit('submit', _(u'Continue &gt;&gt;'),
                       css_class='btn btn-default'),
                css_class='col-lg-offset-2 col-lg-8',
            ),
        )

    def clean(self):
        time_number = self.cleaned_data.get("study_time_number")
        time_unit = self.cleaned_data.get("study_time_unit")

        if time_number and not time_unit:
            raise forms.ValidationError(
                _(u"You have entered a study time, but not selected a unit."))

        return self.cleaned_data

    def clean_description(self):
        description = self.cleaned_data['description']
        no_words = len(strip_tags(description).split(' '))
        if no_words > settings.ORB_RESOURCE_DESCRIPTION_MAX_WORDS:
            raise forms.ValidationError(_(u"You have entered {no_words} words, please enter no more than {max_words}".format(
                no_words=no_words, max_words=settings.ORB_RESOURCE_DESCRIPTION_MAX_WORDS)))
        return description

    def clean_title(self):
        title = self.cleaned_data['title']

        # check if user has already uploaded a resource with this title
        # but only if request object has been passed to form (so only for new
        # Resources
        if not self.request:
            return title

        exists = Resource.objects.filter(
            create_user__pk=self.request.user.id, title=title).count()

        if exists != 0:
            raise forms.ValidationError(
                _(u"You have entered already submitted a resource with this title."))

        return title


class ResourceStep2Form(forms.Form):

    title = forms.CharField(
        required=False,)
    file = forms.FileField(
        required=False,
        error_messages={},)
    url = forms.CharField(
        required=False,
        error_messages={},)

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(ResourceStep2Form, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Row(HTML('<hr>')),
            'title',
            'file',
            'url',
            Div(
                Submit('submit', _(u'Add'), css_class='btn btn-default'),
                css_class='col-lg-offset-2 col-lg-8',
            ),
            Row(HTML('<div style="clear:both;"></div><hr>')),)

    def clean(self):
        file = self.cleaned_data.get("file")
        url = self.cleaned_data.get("url")

        if self._errors:
            raise forms.ValidationError(
                _(u"Please correct the errors below and resubmit the form."))

        if not file and not url:
            raise forms.ValidationError(
                _(u"Please submit a file and/or a url for this resource"))

        return self.cleaned_data

    def clean_file(self):
        file = self.cleaned_data['file']
        if file:
            logger.debug(file.content_type)
            for blacklist in settings.TASK_UPLOAD_FILE_TYPE_BLACKLIST:
                if file.content_type.startswith(blacklist):
                    raise forms.ValidationError(
                        _(u'Currently, ORB does not allow uploading of \'%s\' files' % file.content_type))

            if file._size > settings.TASK_UPLOAD_FILE_MAX_SIZE:
                raise forms.ValidationError(_(u'Please keep filesize under %(max_size)s. Current filesize %(actual_size)s') % {
                                            'max_size': filesizeformat(settings.TASK_UPLOAD_FILE_MAX_SIZE), 'actual_size': filesizeformat(file._size)})

        return file

    def clean_url(self):
        url = self.cleaned_data['url']
        validate = URLValidator()
        if url:
            try:
                validate(url)
            except ValidationError:
                raise forms.ValidationError(
                    _(u"This does not appear to be a valid Url"))
        return url


class SearchForm(forms.Form):
    q = forms.CharField(
        required=True,
        error_messages={'required': _(u'Please enter something to search for')},)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_show_labels = False
        self.helper.form_method = "GET"
        self.helper.form_class = 'form-horizontal'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            FieldWithButtons('q', Submit('submit', _(u'Go'),
                                         css_class='btn btn-default')),

        )


class HeaderSearchForm(forms.Form):
    q = forms.CharField(label="Search:",
                        required=False,
                        error_messages={"required": _(u"Please enter something to search for")},)

    def __init__(self, *args, **kwargs):
        super(HeaderSearchForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "GET"
        self.helper.form_action = 'orb_search'
        self.helper.form_show_labels = False
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-1'
        self.helper.field_class = 'col-lg-4 navbar-right'
        self.helper.layout = Layout(
            FieldWithButtons('q', Submit('submit', _(u"Search"),
                                         css_class='btn btn-default')),
            Row(HTML(u"<a href='{0}'>{1}</a>".format(
                reverse('orb_search_advanced'),
                _(u"Advanced search"),
            )), css_class="advanced-search-link hidden-xs")
        )


class AdvancedSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label=_(u'Search terms'),
        error_messages={'required': _(u'Please enter something to search for')},)
    health_topic = forms.ModelMultipleChoiceField(
        queryset=Tag.tags.all(),
        label=_(u'Health domain'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    resource_type = forms.ModelMultipleChoiceField(
        queryset=Tag.tags.all(),
        label=_(u'Resource type'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    audience = forms.ModelMultipleChoiceField(
        queryset=Tag.tags.all(),
        label=_(u'Audience'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    geography = forms.ModelMultipleChoiceField(
        queryset=Tag.tags.all(),
        label=_(u'Geography'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    language = forms.ModelMultipleChoiceField(
        queryset=Tag.tags.all(),
        label=_(u'Language'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    device = forms.ModelMultipleChoiceField(
        queryset=Tag.tags.all(),
        label=_(u'Device'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    license = forms.MultipleChoiceField(
        choices=[('ND', _(u'Derivatives allowed')), ('NC', _(u'Commercial use allowed'))],
        label=_(u'License'),
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(AdvancedSearchForm, self).__init__(*args, **kwargs)
        self.fields['health_topic'].queryset = Tag.tags.approved().by_category('health-domain').top_level()
        self.fields['resource_type'].queryset = Tag.tags.approved().by_category('type')
        self.fields['audience'].queryset = Tag.tags.approved().by_category('audience')
        self.fields['geography'].queryset = Tag.tags.approved().by_category('geography')
        self.fields['language'].queryset = Tag.tags.approved().by_category('language')
        self.fields['device'].queryset = Tag.tags.approved().by_category('device')
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'q',
            Row(HTML('<hr>')),
            'health_topic',
            Row(HTML('<hr>')),
            'resource_type',
            Row(HTML('<hr>')),
            'audience',
            Row(HTML('<hr>')),
            'geography',
            Row(HTML('<hr>')),
            'language',
            Row(HTML('<hr>')),
            'device',
            Row(HTML('<hr>')),
            'license',
            Row(HTML('<hr>')),
            Div(
                Submit('submit', _(u'Search'),
                       css_class='btn btn-default'),
                css_class='col-lg-offset-2 col-lg-8',
            ),
        )

    def clean(self):
        empty_tags = True
        empty_license = True
        query = self.cleaned_data.get("q", "").strip()

        for name, slug in settings.ADVANCED_SEARCH_CATEGORIES:
            tag_ids = self.cleaned_data.get(name)
            if tag_ids:
                empty_tags = False

        license_ids = self.cleaned_data.get('license')
        if license_ids:
            empty_license = False

        if empty_tags and query == "" and empty_license:
            raise forms.ValidationError(
                _(u"Please select at least a search term or a tag"))

        return self.cleaned_data

    def clean_q(self):
        return self.cleaned_data.get('q', '').strip()

    @cached_property
    def licence_tags(self):
        try:
            return Tag.tags.filter(
                properties__name="feature:shortname",
                properties__value__in=self.cleaned_data['license'],
            )
        except AttributeError:
            return []

    def search(self):
        """
        Implements the filtered search

        Returns:
            a tuple of a queryset and list of Tags

        """
        qs = Resource.resources.approved()
        clean_data = self.cleaned_data
        filter_tags = []
        for field_name in ['health_topic', 'resource_type', 'audience', 'geography', 'language', 'device']:
            if clean_data.get(field_name):
                qs = qs.filter(tags__in=clean_data[field_name])
                filter_tags += clean_data[field_name]

        if clean_data.get('licenses'):
            qs.exclude(tags__in=self.license_tags)

        return qs.distinct(), filter_tags


class ResourceRejectForm(forms.Form):
    criteria = forms.MultipleChoiceField(label=_(u'Criteria'),
                                        widget=forms.CheckboxSelectMultiple,
                                        required=True,)
    notes = forms.CharField(
                        widget=forms.Textarea,
                        required=True,
                        error_messages={'required': _(
                            u'Please enter a reason as to why the resource has been rejected')},
                        help_text=_(u'The text you enter here will be included in the email to the submitter of the resource, so please bear this in mind when explaining your reasoning.'),
                        label=_(u"Reason for rejection")
    )

    def __init__(self, *args, **kwargs):
        super(ResourceRejectForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            'criteria',
            'notes',
            Div(
                Submit('submit', _(u'Submit'),
                       css_class='btn btn-default'),
                css_class='col-lg-offset-2 col-lg-8',
            ),
        )
