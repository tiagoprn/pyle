import logging

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .models import Link

log = logging.getLogger('links')


@receiver(post_save, sender=Link)
def link_saved_handler(sender, instance, created, **kwargs):
    if created:
        message = "Link [id={}] was CREATED.".format(instance.id)
        log.info(message)
    else:
        message = "Link [id={}] was UPDATED.".format(instance.id)
        log.info(message)


@receiver(post_delete, sender=Link)
def link_deleted_handler(sender, instance, using, **kwargs):
    message = 'Link [id={}] was DELETED.'.format(instance.id)
    log.info(message)
