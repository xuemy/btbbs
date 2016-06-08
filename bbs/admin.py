from django.contrib import admin

# Register your models here.
from bbs.models import Movie, Torrent

admin.site.register(Torrent)

class TorrentInline(admin.StackedInline):
    model = Torrent

class MovieAdmin(admin.ModelAdmin):
    inlines = [TorrentInline]

admin.site.register(Movie, MovieAdmin)