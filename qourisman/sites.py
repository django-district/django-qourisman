from django.conf import settings
from django.contrib.admin.sites import AdminSite as OldAdminSite

class AdminSite(OldAdminSite):
    def check_dependencies(self):
        from qourisman.models import LogEntry
        from django.contrib.contenttypes.models import ContentType

        if not LogEntry._meta.installed:
            raise ImproperlyConfigured(
                "Put qourisman in your INSTALLED_APPS setting in order "
                "to use the admin application.")
        if not ContentType._meta.installed:
            raise ImproperlyConfigured(
                "Put 'django.contrib.contenttypes' in your INSTALLED_APPS "
                "setting in order to use the admin application.")
        if not ('django.contrib.auth.context_processors.auth'
                in settings.TEMPLATE_CONTEXT_PROCESSORS or
                'django.core.context_processors.auth'
                in settings.TEMPLATE_CONTEXT_PROCESSORS):
            raise ImproperlyConfigured(
                "Put 'django.contrib.auth.context_processors.auth' "
                "in your TEMPLATE_CONTEXT_PROCESSORS setting in order to "
                "use the admin application.")
    
site = AdminSite()
        
