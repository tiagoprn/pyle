from django.db import models


class Tag(models.Model):
    owner = models.ForeignKey('auth.User', related_name='tags', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    name = models.CharField(max_length=200, unique=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name


class Link(models.Model):
    owner = models.ForeignKey('auth.User', related_name='links', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    url = models.URLField(unique=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    content_last_updated_at = models.DateTimeField(blank=True, null=True)
    tags = models.ManyToManyField(Tag, blank=True, null=True)
