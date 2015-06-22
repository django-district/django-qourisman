# encoding: utf-8
"""
Utility which adds "view only" permissions to the Django admin


This works around the fact the Django core developers are religiously opposed
to adding support for users to see a model which they don't have access to
change (http://code.djangoproject.com/ticket/7150). This is inappropriate for
many large sites and breaks ``raw_id_fields`` when your users have change
access to a model with a relationship to a model for which they lack access
because they will no longer have access to the selection popup.

Due to the invasive nature of this change, you will at the very least need to
update your ModelAdmins to opt-in to this feature. If you intend to allow
global read access you can simply set ``settings.QOURISMAN_STAFF_GLOBAL_VIEW``
to a list of app_labels and avoid needing to register your models as well. In
either case it's recommended that you only opt-in for the models which your
users need so you can avoid information leaks such as being able to retrieve
password hashes by viewing a user's change form.


Installation:

#. Monkeypatch your model admin in your admin.py::

    view_permission.register_admin(model_admin)

#. Optionally register your model in models.py::

    view_permission.register_model(MyModel)
"""

from django.conf import settings


def register_model(model_class):
    model_class._meta.permissions.append(
        ("can_view", "Can view %s" % model_class._meta.verbose_name_raw),
    )


class ViewPermissionMixin(object):
    """
    Update the provided ModelAdmin class to support view permissions

    How it works
    ============

    1. All changes apply only to GET requests, which don't alter data
    2. Only staff users can be granted access at all

    Monkeypatches:
        1. ``ModelAdmin.has_change_permission``
        2. ``ModelAdmin.get_model_perms``
        3. ``ModelAdmin.render_change_form``
        3. ``User.has_module_perms`` - this is called by ``AdminSite.index``
            and ``app_index`` to decide whether to even check the other
            permissions.
    """

    GLOBAL_STAFF_VIEW = getattr(settings, 'QOURISMAN_STAFF_GLOBAL_VIEW', [])

    def has_change_permission(self, request, obj=None):
        res = super(ViewPermissionMixin, self).has_change_permission(request, obj)

        if res:
            return True

        if request.method != 'GET':
            return False

        if not request.user.is_staff:
            return False

        if self.opts.app_label in self.GLOBAL_STAFF_VIEW:
            return True

        return request.user.has_perm('%s.can_view' % self.opts.app_label)

    def get_model_perms(self, request):
        perms = super(ViewPermissionMixin, self).get_model_perms(request)

        perms['view'] = (request.method == 'GET' and request.user.is_staff
                         and (self.opts.app_label in self.GLOBAL_STAFF_VIEW
                              or request.user.has_perm('%s.can_view' % self.opts.app_label)))

        return perms

    def render_change_form(self, request, context, obj=None, *args, **kwargs):
        res = super(ViewPermissionMixin, self).render_change_form(request, context, obj=obj, *args, **kwargs)

        res.context_data.update({
            'has_change_permission': self.has_change_permission(request, obj)
        })

        return res
