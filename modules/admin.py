from django.contrib import admin

from modules.models import Module


# Register your models here.
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'description')
    list_display_links = ('id',)
    search_fields = ('title',)
    list_filter = ('title',)
