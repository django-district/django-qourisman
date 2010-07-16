from django.utils.encoding import smart_unicode
from django.contrib.admin.filterspecs import FilterSpec, RelatedFilterSpec
from django.utils.translation import ugettext_lazy as _
from django.db import models


class NullRelatedFilterSpec(RelatedFilterSpec):
    """
    This is similar to the built-in related filter but includes an option to
    select NULL values

    Based on the snippet at http://djangosnippets.org/snippets/1963/
    """

    def __init__(self, f, request, params, model, model_admin):
        super(NullRelatedFilterSpec, self).__init__(f, request, params, model, model_admin)
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


FilterSpec.filter_specs.insert(0,
    (lambda f: isinstance(f, models.ForeignKey) and getattr(f, "null_related_filter", False), NullRelatedFilterSpec)
)
