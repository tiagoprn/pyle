from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^tags/$', views.TagList.as_view(),
        name=views.TagList.name),
    url(r'^tags/(?P<pk>[0-9]+)/$', views.TagDetail.as_view(),
        name=views.TagDetail.name),

    url(r'^links/$', views.LinkList.as_view(),
        name=views.LinkList.name),
    url(r'^links/(?P<pk>[0-9]+)/$', views.LinkDetail.as_view(),
        name=views.LinkDetail.name),

    url(r'^users/$', views.UserList.as_view(),
        name=views.UserList.name),
    url(r'^users/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(),
        name=views.UserDetail.name),

    url(r'^$', views.ApiRoot.as_view(),
        name=views.ApiRoot.name),
]