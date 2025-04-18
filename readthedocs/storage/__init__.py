"""
Provides lazy loaded storage instances for use throughout Read the Docs.

For static files storage, use django.contrib.staticfiles.storage.staticfiles_storage.
Some storage backends (notably S3) have a slow instantiation time
so doing those upfront improves performance.
"""

from django.conf import settings
from django.core.files.storage import get_storage_class
from django.utils.functional import LazyObject


class ConfiguredBuildMediaStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.RTD_BUILD_MEDIA_STORAGE)()


class ConfiguredBuildCommandsStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.RTD_BUILD_COMMANDS_STORAGE)()


class ConfiguredBuildToolsStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.RTD_BUILD_TOOLS_STORAGE)()


class ConfiguredStaticStorage(LazyObject):
    def _setup(self):
        self._wrapped = get_storage_class(settings.RTD_STATICFILES_STORAGE)()


build_media_storage = ConfiguredBuildMediaStorage()
build_commands_storage = ConfiguredBuildCommandsStorage()
build_tools_storage = ConfiguredBuildToolsStorage()
staticfiles_storage = ConfiguredStaticStorage()
