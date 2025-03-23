from django.urls import path, re_path

from . import views

app_name='items'
urlpatterns = [
    path("", views.item_list_view, name='list'),
    path("<int:id>/", views.item_detail_update_view, name='detail'),
    path("<int:id>/upload/", views.item_upload_view, name='upload'),
    path("<int:id>/files/", views.item_files_view, name='files'),
    re_path(r'^(?P<id>\d+)/files/(?P<n>.*)$', views.item_file_delete_view, name='files_delete'),
    path("<int:id>/edit/", views.item_detail_inline_update_view, name='edit'),
    path("<int:id>/delete/", views.item_delete_view, name='delete'),
    path("create/", views.item_create_view, name='create'),
    # New proxy URLs
    path("<int:id>/view/<str:filename>", views.serve_s3_file, {'as_attachment': False}, name='view_file'),
    path("<int:id>/download/<str:filename>", views.serve_s3_file, {'as_attachment': True}, name='download_file'),
]
