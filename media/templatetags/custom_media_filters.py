from django import template
from ..models import PlayerTime

register = template.Library()

@register.filter
def get_player_time(episode, user):
    return PlayerTime.objects.filter(mediaitem=episode, user=user).first()

@register.filter
def format_playertime(seconds_str):
    try:
        # Convert seconds_str to integer
        seconds = int(seconds_str)
        # Calculate hours, minutes, and seconds
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)

        # Format the result
        if hours > 0:
            return "{:02d}:{:02d}:{:02d}".format(int(hours), int(minutes), int(seconds))
        else:
            return "{:02d}:{:02d}".format(int(minutes), int(seconds))
    except:
        return ""
