#!/usr/bin/env python
# coding: utf-8
# Copyright (c) 2012 Baina Info Inc. All rights reserved.
# @Author : Jun Wang
# @Date : 2012-7-10
# Email: jwang@bainainfo.com

import logging
from django.contrib import admin
from dolphinopadmin.base.admin import ToolAdmin
from dolphinopadmin.configure.models import Package, Source, SourceSet, Locale, LocaleSet, \
    VersionCode, OSVersion, OSVersionSet, Mobile, MobileSet, CPU, CPUSet, \
    Operator, Location, Rule
from dolphinopadmin.utils.sites import custom_site

logger = logging.getLogger("dolphinopadmin.admin")


class PackageAdmin(ToolAdmin):

    list_display = ('id', 'name', 'uid')
    list_display_links = ['name']
    ordering = ['-id']


class SourceSetAdmin(ToolAdmin):

    list_display = ('id', 'name', 'exclude')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ['name']
    filter_horizontal = ['sources']


class SourceAdmin(ToolAdmin):

    list_display = ('id', 'source')
    list_display_links = ['source']
    ordering = ['-id']
    search_fields = ['source']


class LocaleSetAdmin(ToolAdmin):

    list_display = ('id', 'name', 'exclude')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ['name']
    filter_horizontal = ['locales']


class LocaleAdmin(ToolAdmin):

    list_display = ('id', 'locale')
    list_display_links = ['locale']
    ordering = ['-id']
    search_fields = ['locale']


class VersionCodeAdmin(ToolAdmin):

    list_display = ('id', 'package', 'version', 'vname')
    ordering = ['-id']
    search_fields = ['version', 'vname']


class OSVersionAdmin(ToolAdmin):

    list_display = ('id', 'os_version')
    list_display_links = ['os_version']
    ordering = ['-id']
    search_fields = ['os_version']


class OSVersionSetAdmin(ToolAdmin):

    list_display = ('id', 'name', 'exclude')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ['name']
    filter_horizontal = ['os_versions']


class MobileAdmin(ToolAdmin):

    list_display = ('id', 'mobile')
    list_display_links = ['mobile']
    ordering = ['-id']
    search_fields = ['mobile']


class MobileSetAdmin(ToolAdmin):

    list_display = ('id', 'name', 'exclude')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ['name']
    filter_horizontal = ['mobiles']


class CPUAdmin(ToolAdmin):

    list_display = ('id', 'cpu')
    list_display_links = ['cpu']
    ordering = ['-id']
    search_fields = ['cpu']


class CPUSetAdmin(ToolAdmin):

    list_display = ('id', 'name', 'exclude')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ['name']
    filter_horizontal = ['cpus']


class OperatorAdmin(ToolAdmin):

    list_display = ('id', 'operator', 'code')
    list_display_links = ['operator']
    ordering = ['-id']
    search_fields = ['operator', 'code']


class LocationAdmin(ToolAdmin):

    list_display = ('id', 'name', 'location')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ('name', 'location')


class RuleAdmin(ToolAdmin):

    list_display = ('id', 'name', 'min_version', 'max_version')
    list_display_links = ['name']
    ordering = ['-id']
    search_fields = ('name', 'min_version', 'max_version')
    filter_horizontal = ('packages', 'operators',
                         'sources', 'locales', 'locations')


custom_site.register(Package, PackageAdmin)
custom_site.register(Source, SourceAdmin)
custom_site.register(SourceSet, SourceSetAdmin)
custom_site.register(Locale, LocaleAdmin)
custom_site.register(LocaleSet, LocaleSetAdmin)
custom_site.register(VersionCode, VersionCodeAdmin)
custom_site.register(OSVersion, OSVersionAdmin)
custom_site.register(OSVersionSet, OSVersionSetAdmin)
custom_site.register(Mobile, MobileAdmin)
custom_site.register(MobileSet, MobileSetAdmin)
custom_site.register(CPU, CPUAdmin)
custom_site.register(CPUSet, CPUSetAdmin)
custom_site.register(Operator, OperatorAdmin)
custom_site.register(Location, LocationAdmin)
custom_site.register(Rule, RuleAdmin)
