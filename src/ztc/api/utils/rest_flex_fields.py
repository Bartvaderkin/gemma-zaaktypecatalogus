import importlib

import coreapi
from rest_flex_fields.views import FlexFieldsMixin as _FlexFieldsMixin
from rest_framework.schemas import AutoSchema


class FlexFieldsMixin(_FlexFieldsMixin):
    """
    Extended the original mixin to insert the `expand` and `fields` parameters to the documentation.
    """
    # These are not picked up by `drf_openapi` version 1.3. Hence, we our own fork.
    # See: https://github.com/limdauto/drf_openapi/issues/116
    schema = AutoSchema(
        manual_fields=[
            coreapi.Field('expand', description='Which field(s) to expand. Multiple fields can be separated with a comma.'),
            coreapi.Field('fields', description='Which field(s) to show. Multiple fields can be separated with a comma.'),
        ]
    )


class FlexFieldsSerializerMixin(object):
    """
    Copy of the `rest_flex_fields.serializers.FlexFieldsModelSerializer` class but as a mixin to be more flexible.

    Other changes:

        * Changed `?expand=~all` to `?expand=true`.
        * Added feature to add the name to the inclusion fields, if its not expandable.

    """
    expandable_fields = {}

    def __init__(self, *args, **kwargs):
        expand_field_names = self._get_dynamic_setting(kwargs, 'expand')
        include_field_names = self._get_dynamic_setting(kwargs, {'class_property': 'include_fields', 'kwargs': 'fields'})
        expand_field_names, next_expand_field_names = self._split_levels(expand_field_names)
        include_field_names, next_include_field_names = self._split_levels(include_field_names)
        self._expandable = self.expandable_fields.keys()
        self.expanded_fields = []

        # Instantiate the superclass normally
        super(FlexFieldsSerializerMixin, self).__init__(*args, **kwargs)

        # Added feature to add the name to the inclusion fields, if its not expandable.
        for name in expand_field_names:
            if name in self.fields.keys() and name not in self._expandable:
                include_field_names.append(name)

        self._clean_fields(include_field_names)

        # Changed `?expand=~all` to `?expand=true`.
        if 'true' in expand_field_names:
            expand_field_names = self.expandable_fields.keys()

        for name in expand_field_names:
            if name not in self._expandable:
                continue

            self.expanded_fields.append(name)
            self.fields[name] = self._make_expanded_field_serializer(
                name, next_expand_field_names, next_include_field_names
            )

    def _make_expanded_field_serializer(self, name, nested_expands, nested_includes):
        """
        Returns an instance of the dynamically created embedded serializer.
        """
        import copy
        field_options = self.expandable_fields[name]
        serializer_class = field_options[0]
        serializer_settings = copy.deepcopy(field_options[1])

        if name in nested_expands:
            serializer_settings['expand'] = nested_expands[name]

        if name in nested_includes:
            serializer_settings['fields'] = nested_includes[name]

        if serializer_settings.get('source') == name:
            del serializer_settings['source']

        if type(serializer_class) == str:
            serializer_class = self._import_serializer_class(serializer_class)

        return serializer_class(**serializer_settings)

    def _import_serializer_class(self, location):
        """
        Resolves dot-notation string reference to serializer class and returns actual class.

        <app>.<SerializerName> will automatically be interpreted as <app>.serializers.<SerializerName>
        """
        pieces = location.split('.')
        class_name = pieces.pop()
        if pieces[ len(pieces)-1 ] != 'serializers':
            pieces.append('serializers')

        module = importlib.import_module( '.'.join(pieces) )
        return getattr(module, class_name)

    def _clean_fields(self, include_fields):
        if include_fields:
            allowed_fields = set(include_fields)
            existing_fields = set(self.fields.keys())
            existing_expandable_fields = set(self.expandable_fields.keys())

            for field_name in existing_fields - allowed_fields:
                self.fields.pop(field_name)

            self._expandable = list( existing_expandable_fields & allowed_fields )

    def _split_levels(self, fields):
        """
            Convert dot-notation such as ['a', 'a.b', 'a.d', 'c'] into current-level fields ['a', 'c']
            and next-level fields {'a': ['b', 'd']}.
        """
        first_level_fields = []
        next_level_fields = {}

        if not fields:
            return first_level_fields, next_level_fields

        if not isinstance(fields, list):
            fields = [a.strip() for a in fields.split(',') if a.strip()]
        for e in fields:
            if '.' in e:
                first_level, next_level = e.split('.', 1)
                first_level_fields.append(first_level)
                next_level_fields.setdefault(first_level, []).append(next_level)
            else:
                first_level_fields.append(e)

        first_level_fields = list(set(first_level_fields))
        return first_level_fields, next_level_fields

    def _get_dynamic_setting(self, passed_settings, source):
        """
            Returns value of dynamic setting.

            The value can be set in one of two places:
            (a) The originating request's GET params; it is then defined on the serializer class
            (b) Manually when a nested serializer field is defined; it is then passed in the serializer class constructor
        """
        if isinstance(source, dict):
            if hasattr(self, source['class_property']):
                return getattr(self, source['class_property'])

            return passed_settings.pop(source['kwargs'], None)
        else:
            if hasattr(self, source):
                return getattr(self, source)

            return passed_settings.pop(source, None)