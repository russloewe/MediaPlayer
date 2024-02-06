from django.urls import path

from . import views

app_name = 'media'

urlpatterns = [
    path('play/<slug:slug>', views.MediaView.as_view(), name='play_media'),
    path('playing/<int:mediaitem_id>/<int:position>', views.UpdatePlayerTimeView.as_view(), name='player_time'),
    path('playing/clear/<int:mediaitem_id>', views.ClearPlayerTimeView.as_view(), name='player_time'),
    path('series/<slug:slug>', views.SeriesDetailView.as_view(), name='series_detail'),
    path('', views.SeriesListView.as_view(), name='series_list'),
]
