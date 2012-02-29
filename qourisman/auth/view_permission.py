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

from functools import wraps

from django.conf import settings
from django.contrib.auth.models import User


def register_model(model_class):
    model_class._meta.permissions.append(
        ("can_view", "Can view %s" % model_class._meta.verbose_name_raw),
    )


def register_admin(model_admin):
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

    old_has_change_permission = model_admin.has_change_permission

    global_staff_view = getattr(settings, "QOURISMAN_STAFF_GLOBAL_VIEW", [])

    if any(global_staff_view):
        # Monkeypatch the User class so we can make has_module_perms work:
        old_has_module_perms = User.has_module_perms

        @wraps(old_has_module_perms)
        def new_has_module_perms(self, app_label):
            if not self.is_staff:
                return False

            if app_label in global_staff_view:
                return True
            else:
                return old_has_module_perms(self, app_label)

        User.has_module_perms = new_has_module_perms

    @wraps(old_has_change_permission)
    def new_has_change_permission(self, request, obj=None):
        res = old_has_change_permission(self, request, obj)

        if res:
            return True

        if request.method != "GET":
            return False

        if not request.user.is_staff:
            return False

        if self.opts.app_label in global_staff_view:
            return True

        return request.user.has_perm('%s.can_view' % self.opts.app_label)

    model_admin.has_change_permission = new_has_change_permission

    old_get_model_perms = model_admin.get_model_perms

    @wraps(old_get_model_perms)
    def new_get_model_perms(self, request):
        perms = old_get_model_perms(self, request)

        perms['view'] = (request.method == "GET"
            and request.user.is_staff
            and (self.opts.app_label in global_staff_view
                or request.user.has_perm('%s.can_view' % self.opts.app_label)))

        return perms

    model_admin.get_model_perms = new_get_model_perms


    from django.shortcuts import render_to_response
    from django.utils.safestring import mark_safe
    from django import template
    from django.contrib.contenttypes.models import ContentType
    
    old_render_change_form = model_admin.render_change_form
    
    # this is exactly the same as render_change_form, except it calls old_has_change_permission
    # This is necessary to hide "Save (...)" buttons 
    @wraps(old_render_change_form)
    def new_render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': old_has_change_permission(self, request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': self.admin_site.root_path,
        })
        if add and self.add_form_template is not None:
            form_template = self.add_form_template
        else:
            form_template = self.change_form_template
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        return render_to_response(form_template or [
            "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
            "admin/%s/change_form.html" % app_label,
            "admin/change_form.html"
        ], context, context_instance=context_instance)
        
    model_admin.render_change_form = new_render_change_form
