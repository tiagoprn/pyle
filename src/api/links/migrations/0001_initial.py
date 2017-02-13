# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-02-13 19:16
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Link',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('uri', models.URLField()),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('notes', models.TextField(blank=True, null=True)),
                ('content', models.TextField(blank=True, null=True)),
                ('content_last_updated_at', models.DateTimeField(blank=True, null=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='links', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-created',),
            },
        ),
        migrations.CreateModel(
            name='LinkTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('link', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='links.Link')),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('name', models.CharField(max_length=200)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tags', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='linktag',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='links.Tag'),
        ),
        migrations.AddField(
            model_name='link',
            name='tags',
            field=models.ManyToManyField(related_name='links', through='links.LinkTag', to='links.Tag'),
        ),
        migrations.AlterIndexTogether(
            name='tag',
            index_together=set([('owner', 'name'), ('owner', 'created')]),
        ),
        migrations.AlterUniqueTogether(
            name='link',
            unique_together=set([('owner', 'uri')]),
        ),
        migrations.AlterIndexTogether(
            name='link',
            index_together=set([('owner', 'name'), ('owner', 'uri'), ('owner', 'created'), ('owner', 'content_last_updated_at')]),
        ),
    ]
