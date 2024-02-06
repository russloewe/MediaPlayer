from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
#from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.db.models import Count
from django.http import JsonResponse
from .models import Series, MediaItem, PlayerTime
  
class UpdatePlayerTimeView(View):
    def get(self, request, mediaitem_id, position):
        # mediaitem_id = kwargs.get('mediaitem_id')
        # position = request.POST.get('position')

        # Retrieve the MediaItem object
        mediaitem = get_object_or_404(MediaItem, id=mediaitem_id)

        # Check if a PlayerTime object already exists for the user and mediaitem
        player_time, created = PlayerTime.objects.get_or_create(
            user=request.user,
            mediaitem=mediaitem,
            local_path=mediaitem.local_path,
            defaults={'position': position}
        )

        # If the object already exists, update the position
        if not created and player_time.position != position:
            player_time.position = position
            player_time.save()

        return JsonResponse({'status': 'success'})

class ClearPlayerTimeView(View):
    def get(self, request, mediaitem_id):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Access Forbidden")
            
        # Retrieve the MediaItem object
        mediaitem = get_object_or_404(MediaItem, id=mediaitem_id)

       # Delete all PlayerTime objects for the user and mediaitem
        PlayerTime.objects.filter(user=request.user, mediaitem=mediaitem).delete()
        
        return JsonResponse({'status': 'success'})


class SeriesListView(View):
    template_name = 'media/series_list.html'

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Access Forbidden")
            
        # Get all series and media items without a series
        all_series = Series.objects.all()
        standalone_media_items = MediaItem.objects.filter(series__isnull=True)
        
        # Pre-process player times for each episode
        player_times = {}
        for episode in standalone_media_items:
            player_time = episode.playertime_set.filter(user=request.user).first()
            player_times[episode.id] = player_time.position if player_time else None

        context = {
            'all_series': all_series,
            'standalone_media_items': standalone_media_items,
            'player_times': player_times,
        }

        return render(request, self.template_name, context)

class SeriesDetailView(View):
    template_name = 'media/series_detail.html'

    def get(self, request, slug):
        if not request.user.is_authenticated:
            return HttpResponseForbidden("Access Forbidden")
            
        series = get_object_or_404(Series, slug=slug)
        episodes = MediaItem.objects.filter(series=series).order_by('episode')
        # Pre-process player times for each episode
        player_times = {}
        for episode in episodes:
            player_time = episode.playertime_set.filter(user=request.user).first()
            player_times[episode.id] = player_time.position if player_time else None


        context = {
            'series': series,
            'episodes': episodes,
            'play_times': player_times,
        }

        return render(request, self.template_name, context)
        
class MediaView(View):
    template_name = 'media/play_media.html'
    
    def get(self, request, slug):
        if request.user.is_authenticated:
            # Serve the video content
            media_item = get_object_or_404(MediaItem, slug=slug)
            
            # Check if there's an existing PlayerTime object for the current user and mediaitem
            player_time = PlayerTime.objects.filter(user=request.user, mediaitem=media_item).first()

            # Check if the MediaItem is part of a series
            if media_item.series:
                series_object = media_item.series
                
                # Get the previous episode if it exists
                previous_episode = MediaItem.objects.filter(series=series_object, episode__lt=media_item.episode).order_by('-episode').first()

                # Get the next episode if it exists
                next_episode = MediaItem.objects.filter(series=series_object, episode__gt=media_item.episode).order_by('episode').first()

                context = {
                    'media_item': media_item,
                    'series': series_object,
                    'previous_episode': previous_episode,
                    'next_episode': next_episode,
                    'player_time': player_time,
                }
                
                # You may want to include additional logic here based on the series
                return render(request, self.template_name, context)
            else:
                
                context = {'media_item': media_item,
                            'player_time': player_time,
                }
                
                return render(request, self.template_name, context)

            return HttpResponse("Media content here")
        else:
            return HttpResponseForbidden("Access Forbidden")
