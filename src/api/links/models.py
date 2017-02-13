from django.db import models


class Tag(models.Model):
    owner = models.ForeignKey('auth.User', related_name='tags', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200)

    class Meta:
        ordering = ('name',)
        index_together = [['owner', 'name'],
                          ['owner', 'created']]

    def __str__(self):
        return self.name


class Link(models.Model):
    owner = models.ForeignKey('auth.User', related_name='links', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    uri = models.URLField()
    name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_last_updated_at = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag,
                                  related_name='links',
                                  through='LinkTag',
                                  through_fields=('link', 'tag'))

    class Meta:
        ordering = ('-created',)
        unique_together = (('owner', 'uri'),)
        index_together = [['owner', 'uri'],
                          ['owner', 'name'],
                          ['owner', 'created'],
                          ['owner', 'content_last_updated_at']]

    def __str__(self):
        return self.name or self.url


class LinkTag(models.Model):
    link = models.ForeignKey(Link, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'Link: {}, Tag: {}'.format(self.link.name,
                                          self.tag.name)
