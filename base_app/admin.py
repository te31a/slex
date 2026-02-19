from django.contrib import admin
from base_app.models import Filial, Menu, Contracts


class FilialAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class MenuAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class ContractsAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


admin.site.register(Filial, FilialAdmin)
admin.site.register(Menu, MenuAdmin)
admin.site.register(Contracts, ContractsAdmin)
