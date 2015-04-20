# orb/urls.py
from django.conf import settings
from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView

from orb.api.resources import ResourceResource, TagResource, ResourceTagResource, ResourceURLResource
from orb.feeds import LatestTagEntries, LatestEntries

from tastypie.api import Api


v1_api = Api(api_name='v1')
v1_api.register(ResourceResource())
v1_api.register(TagResource())
v1_api.register(ResourceTagResource())
v1_api.register(ResourceURLResource())

urlpatterns = patterns('',

    url(r'^$', 'orb.views.home_view', name="orb_home"),
    
    url(r'^about/$',TemplateView.as_view(template_name="orb/about.html"), name="orb_about"),
    url(r'^developers/$',TemplateView.as_view(template_name="orb/developers.html"), name="orb_developers"),
    url(r'^feed/$', LatestEntries() , name="orb_feed"),
    url(r'^partners/$', 'orb.views.partner_view', name="orb_partners"),
    url(r'^taxonomy/$', 'orb.views.taxonomy_view', name="orb_taxonomy"),
    url(r'^terms/$',TemplateView.as_view(template_name="orb/terms.html"), name="orb_terms"),
    
    url(r'^profile/', include('orb.profile.urls')),
    
    url(r'^tag/view/(?P<tag_slug>\w[\w/-]*)$', 'orb.views.tag_view', name="orb_tags"),
    url(r'^tag/cloud/$', 'orb.views.tag_cloud_view', name="orb_tag_cloud"),
    url(r'^tag/feed/(?P<tag_slug>\w[\w/-]*)$', LatestTagEntries() , name="orb_tag_feed"),
    url(r'^tag/filter/$', 'orb.views.tag_filter_view', name="orb_tags_filter"),
    url(r'^tag/filter/(?P<tag_id>\d+)/$', 'orb.views.tag_filter_prefill_view', name="orb_tags_filter_prefill"),
    url(r'^tag/filter/results$', 'orb.views.tag_filter_results_view', name="orb_tags_filter_results"),
    
    url(r'^resource/create/$', 'orb.views.resource_create_view', name="orb_resource_create"),
    url(r'^resource/create/(?P<id>\d+)/thanks/$', 'orb.views.resource_create_thanks_view', name="orb_resource_create_thanks"),
    url(r'^resource/view/(?P<resource_slug>\w[\w/-]*)$', 'orb.views.resource_view', name="orb_resource"),
    url(r'^resource/(?P<id>\d+)$', 'orb.views.resource_permalink_view', name="orb_resource_permalink"),
    url(r'^resource/link/(?P<id>\d+)/$', 'orb.views.resource_link_view', name="orb_resource_view_link"),
    url(r'^resource/file/(?P<id>\d+)/$', 'orb.views.resource_file_view', name="orb_resource_view_file"),
    url(r'^resource/edit/(?P<resource_id>\d+)/$', 'orb.views.resource_edit_view', name="orb_resource_edit"),
    url(r'^resource/edit/(?P<id>\d+)/thanks/$', 'orb.views.resource_edit_thanks_view', name="orb_resource_edit_thanks"),
   
    url(r'^resource/approve/(?P<id>\d+)/$', 'orb.views.resource_approve_view', name="orb_resource_approve"),
    url(r'^resource/pending_mep/(?P<id>\d+)/$', 'orb.views.resource_pending_mep_view', name="orb_resource_pending_mep"),
    url(r'^resource/reject/(?P<id>\d+)/$', 'orb.views.resource_reject_view', name="orb_resource_reject"),
    
    url(r'^resource/rate/$', 'orb.views.resource_rate_view', name="orb_resource_rate"),
    url(r'^resource/guidelines/$',TemplateView.as_view(template_name="orb/resource/guidelines.html"), name="orb_guidelines"),
    
    
    url(r'^analytics/', include('orb.analytics.urls')),
    
    url(r'^tinymce/', include('tinymce.urls')),
    url(r'^search/$', 'orb.views.search_view', name="orb_search"),
    url(r'^opensearch/$', TemplateView.as_view(template_name="search/opensearch.html"), name="orb_opensearch"),
    
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/upload/image/$', 'orb.api.upload.image_view', name="orb_image_upload"),
    url(r'^api/upload/file/$', 'orb.api.upload.file_view', name="orb_file_upload"),
    
)
