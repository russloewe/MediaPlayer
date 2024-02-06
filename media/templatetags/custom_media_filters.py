from django import template
from ..models import PlayerTime

register = template.Library()

@register.filter
def get_player_time(episode, user):
    return PlayerTime.objects.filter(mediaitem=episode, user=user).first()
