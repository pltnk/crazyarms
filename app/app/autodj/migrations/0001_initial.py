# Generated by Django 3.1.4 on 2020-12-20 23:07

import common.models
import datetime
import dirtyfields.dirtyfields
from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AudioAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('title', common.models.TruncatingCharField(blank=True, db_index=True, help_text="If left empty, a title will be generated from the file's metadata.", max_length=255, verbose_name='title')),
                ('file_basename', models.CharField(max_length=512)),
                ('file', models.FileField(blank=True, help_text='You can provide either an uploaded audio file or a URL to an external asset.', max_length=512, upload_to=common.models.audio_asset_file_upload_to, verbose_name='audio file')),
                ('duration', models.DurationField(default=datetime.timedelta(0), verbose_name='Audio duration')),
                ('fingerprint', models.UUIDField(db_index=True, null=True)),
                ('status', models.CharField(choices=[('-', 'processing queued'), ('p', 'processing'), ('f', 'processing failed'), ('r', 'ready for play')], db_index=True, default='-', help_text='You will be able to edit this asset when status is "ready for play."', max_length=1, verbose_name='status')),
                ('task_id', models.UUIDField(null=True)),
                ('artist', common.models.TruncatingCharField(blank=True, help_text="If left empty, an artist will be generated from the file's metadata.", max_length=255, verbose_name='artist')),
                ('album', common.models.TruncatingCharField(blank=True, help_text="If left empty, an album will be generated from the file's metadata.", max_length=255, verbose_name='album')),
                ('title_normalized', common.models.TruncatingCharField(db_index=True, max_length=255)),
                ('artist_normalized', common.models.TruncatingCharField(db_index=True, max_length=255)),
                ('album_normalized', common.models.TruncatingCharField(db_index=True, max_length=255)),
                ('uploader', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploader')),
            ],
            options={
                'verbose_name': 'audio asset',
                'verbose_name_plural': 'audio assets',
                'ordering': ('title', 'artist', 'album', 'id'),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.CreateModel(
            name='Rotator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
            ],
            options={
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Stopset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('weight', models.FloatField(default=1.0, help_text="The weight (ie selection bias) for how likely random selection from this playlist/stopset occurs, eg '1.0' is just as likely as all others, '2.0' is 2x as likely, '3.0' is 3x as likely, '0.5' half as likely, and so on. If unsure, leave as '1.0'.", validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='random weight')),
                ('is_active', models.BooleanField(default=True, help_text='Whether tracks from this playlist/stopset will be selected. You may want to enable special playlists/stopsets at certain times, for example during the holidays.', verbose_name='currently active')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='StopsetRotator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rotator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='autodj.rotator')),
                ('stopset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='autodj.stopset')),
            ],
            options={
                'verbose_name': 'rotator in stop set relationship',
                'verbose_name_plural': 'rotator in stop set relationships',
                'ordering': ('id',),
            },
        ),
        migrations.CreateModel(
            name='RotatorAsset',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='last modified')),
                ('title', common.models.TruncatingCharField(blank=True, db_index=True, help_text="If left empty, a title will be generated from the file's metadata.", max_length=255, verbose_name='title')),
                ('file_basename', models.CharField(max_length=512)),
                ('file', models.FileField(blank=True, help_text='You can provide either an uploaded audio file or a URL to an external asset.', max_length=512, upload_to=common.models.audio_asset_file_upload_to, verbose_name='audio file')),
                ('duration', models.DurationField(default=datetime.timedelta(0), verbose_name='Audio duration')),
                ('fingerprint', models.UUIDField(db_index=True, null=True)),
                ('status', models.CharField(choices=[('-', 'processing queued'), ('p', 'processing'), ('f', 'processing failed'), ('r', 'ready for play')], db_index=True, default='-', help_text='You will be able to edit this asset when status is "ready for play."', max_length=1, verbose_name='status')),
                ('task_id', models.UUIDField(null=True)),
                ('uploader', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='uploader')),
            ],
            options={
                'verbose_name': 'rotator asset',
                'verbose_name_plural': 'rotator assets',
                'ordering': ('title', 'id'),
            },
            bases=(dirtyfields.dirtyfields.DirtyFieldsMixin, models.Model),
        ),
        migrations.AddField(
            model_name='rotator',
            name='rotator_assets',
            field=models.ManyToManyField(blank=True, db_index=True, related_name='rotators', to='autodj.RotatorAsset', verbose_name='rotator assets'),
        ),
        migrations.CreateModel(
            name='Playlist',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='name')),
                ('weight', models.FloatField(default=1.0, help_text="The weight (ie selection bias) for how likely random selection from this playlist/stopset occurs, eg '1.0' is just as likely as all others, '2.0' is 2x as likely, '3.0' is 3x as likely, '0.5' half as likely, and so on. If unsure, leave as '1.0'.", validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='random weight')),
                ('is_active', models.BooleanField(default=True, help_text='Whether tracks from this playlist/stopset will be selected. You may want to enable special playlists/stopsets at certain times, for example during the holidays.', verbose_name='currently active')),
                ('audio_assets', models.ManyToManyField(blank=True, db_index=True, related_name='playlists', to='autodj.AudioAsset', verbose_name='audio assets')),
            ],
            options={
                'ordering': ('name',),
                'abstract': False,
            },
        ),
    ]
