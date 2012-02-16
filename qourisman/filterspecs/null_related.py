from django.conf import settings
from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec, ChoicesFilterSpec
from django.db import models
from django.utils.encoding import smart_unicode
from django.utils.translation import ugettext_lazy as _


class NullValueFilter(RelatedFilterSpec):
    """
    This avoids the performance anti-pattern of displaying a large number of
    choices when all you need is a simple defined/undefined check
    """

    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        super(NullValueFilter, self).__init__(f, request, params, model,
                                                model_admin, *args, **kwargs)
        self.lookup_kwarg = '%s__isnull' % f.name
        self.lookup_val = request.GET.get(self.lookup_kwarg, None)

    def has_output(self):
        return True

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg]),
            'display': _('All')
        }

        yield {
            'selected': self.lookup_val == "False",
            'query_string': cl.get_query_string({self.lookup_kwarg: False}, [self.lookup_kwarg]),
            'display': _('Assigned')
        }

        yield {
            'selected': self.lookup_val == "True",
            'query_string': cl.get_query_string({self.lookup_kwarg: True}, [self.lookup_kwarg]),
            'display': _('Unassigned')
        }


class NullChoicesFilterSpec(ChoicesFilterSpec):
    """
    This is similar to the built-in related choices but includes an option to
    select NULL values
    """

    def __init__(self, f, request, params, model, model_admin,
                 field_path=None):
        super(NullChoicesFilterSpec, self).__init__(f, request, params, model, model_admin, field_path=field_path)
        self.lookup_null_kwarg = '%s__isnull' % self.field_path
        self.lookup_null = request.GET.get(self.lookup_null_kwarg, False)

    def has_output(self):
        # Force this to be true so we'll display the All and Unspecified
        # options even if there are no other choices:
        return True

    def choices(self, cl):
        i = super(NullChoicesFilterSpec, self).choices(cl)

        i.next()  # Discard "All" choice since we need our additional check for !NULL

        yield {
            'selected': self.lookup_val is None and not self.lookup_null,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_null_kwarg]),
            'display': _('All')
        }

        yield {
            'selected': self.lookup_val is None and self.lookup_null,
            'query_string': cl.get_query_string({self.lookup_null_kwarg: True}, [self.lookup_kwarg]),
            'display': _('Unspecified')
        }

        for j in i:
            yield j

    @classmethod
    def can_handle_field(cls, f):
        print f.name
        return getattr(f, "null_choices_filter", False)


class NullRelatedFilterSpec(RelatedFilterSpec):
    """
    This is similar to the built-in related filter but includes an option to
    select NULL values

    Based on the snippet at http://djangosnippets.org/snippets/1963/
    """

    def __init__(self, f, request, params, model, model_admin, *args, **kwargs):
        super(NullRelatedFilterSpec, self).__init__(f, request, params, model,
                model_admin, *args, **kwargs)
        self.lookup_choices = f.get_choices(include_blank=False)
        self.lookup_null_kwarg = '%s__isnull' % f.name
        self.lookup_null = request.GET.get(self.lookup_null_kwarg, False)

    def has_output(self):
        # Force this to be true so we'll display the All and Unspecified
        # options even if there are no other choices:
        return True

    def choices(self, cl):
        yield {
            'selected': self.lookup_val is None and not self.lookup_null,
            'query_string': cl.get_query_string({}, [self.lookup_kwarg, self.lookup_null_kwarg]),
            'display': _('All')
        }

        yield {
            'selected': self.lookup_val is None and self.lookup_null,
            'query_string': cl.get_query_string({self.lookup_null_kwarg: True}, [self.lookup_kwarg]),
            'display': _('Unspecified')
        }

        for pk_val, val in self.lookup_choices:
            yield {
                'selected': self.lookup_val == smart_unicode(pk_val),
                'query_string': cl.get_query_string({self.lookup_kwarg: pk_val}, [self.lookup_null_kwarg]),
                'display': val
            }

    @classmethod
    def can_handle_field(cls, f):
        if not isinstance(f, models.ForeignKey) or not f.null:
            return False

        if getattr(f, "null_related_filter", False):
            return True

        return getattr(settings, "QOURISMAN_GLOBAL_NULL_RELATED_FILTER", True)


FilterSpec.filter_specs.insert(0,
    (NullRelatedFilterSpec.can_handle_field, NullRelatedFilterSpec)
)

FilterSpec.filter_specs.insert(0,
    (NullChoicesFilterSpec.can_handle_field, NullChoicesFilterSpec)
)

FilterSpec.filter_specs.insert(0,
    (lambda f: getattr(f, "null_value_filter", False), NullValueFilter)
)
