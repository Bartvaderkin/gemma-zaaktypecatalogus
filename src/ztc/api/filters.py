from django.utils.translation import ugettext_lazy as _

from django_filters import rest_framework as filters
from vng_api_common.filtersets import FilterSet
from vng_api_common.utils import get_resource_for_path

from ztc.datamodel.models import (
    BesluitType, Catalogus, Eigenschap, InformatieObjectType, ResultaatType,
    RolType, StatusType, ZaakInformatieobjectType, ZaakType
)

# custom filter to show concept and non-concepts
STATUS_HELP_TEXT = """filter objects depending on their concept status:
* `alles`: Toon objecten waarvan het attribuut `concept` true of false is.
* `concept`: Toon objecten waarvan het attribuut `concept` true is.
* `definitief`: Toon objecten waarvan het attribuut `concept` false is (standaard).
"""


def status_filter(queryset, name, value):
    if value == 'concept':
        return queryset.filter(**{name: True})
    elif value == 'definitief':
        return queryset.filter(**{name: False})
    elif value == 'alles':
        return queryset


def m2m_filter(queryset, name, value):
    object = get_resource_for_path(value)
    return queryset.filter(**{name: object})


class CharArrayFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class RolTypeFilter(FilterSet):
    status = filters.CharFilter(field_name='zaaktype__concept', method=status_filter, help_text=STATUS_HELP_TEXT)

    class Meta:
        model = RolType
        fields = (
            'zaaktype',
            'omschrijving_generiek',
            'status'
        )


class ZaakInformatieobjectTypeFilter(FilterSet):
    status = filters.CharFilter(field_name='zaaktype__concept', method='status_filter_m2m', help_text=STATUS_HELP_TEXT)

    class Meta:
        model = ZaakInformatieobjectType
        fields = (
            'zaaktype',
            'informatieobjecttype',
            'richting',
            'status',
        )

    def status_filter_m2m(self, queryset, name, value):
        if value == 'concept':
            return queryset.filter(zaaktype__concept=True, informatieobjecttype__concept=True)
        elif value == 'definitief':
            return queryset.filter(zaaktype__concept=False, informatieobjecttype__concept=False)
        elif value == 'alles':
            return queryset


class ResultaatTypeFilter(FilterSet):
    status = filters.CharFilter(field_name='zaaktype__concept', method=status_filter, help_text=STATUS_HELP_TEXT)

    class Meta:
        model = ResultaatType
        fields = (
            'zaaktype',
            'status'
        )


class StatusTypeFilter(FilterSet):
    status = filters.CharFilter(field_name='zaaktype__concept', method=status_filter, help_text=STATUS_HELP_TEXT)

    class Meta:
        model = StatusType
        fields = (
            'zaaktype',
            'status'
        )


class EigenschapFilter(FilterSet):
    status = filters.CharFilter(field_name='zaaktype__concept', method=status_filter, help_text=STATUS_HELP_TEXT)

    class Meta:
        model = Eigenschap
        fields = (
            'zaaktype',
            'status'
        )


class ZaakTypeFilter(FilterSet):
    status = filters.CharFilter(field_name='concept', method=status_filter, help_text=STATUS_HELP_TEXT)
    trefwoorden = CharArrayFilter(field_name='trefwoorden', lookup_expr='contains')
    identificatie = filters.NumberFilter(field_name='zaaktype_identificatie')

    class Meta:
        model = ZaakType
        fields = (
            'catalogus',
            'identificatie',
            'trefwoorden',
            'status'
        )


class InformatieObjectTypeFilter(FilterSet):
    status = filters.CharFilter(field_name='concept', method=status_filter, help_text=STATUS_HELP_TEXT)

    class Meta:
        model = InformatieObjectType
        fields = (
            'catalogus',
            'status'
        )


class BesluitTypeFilter(FilterSet):
    zaaktypes = filters.CharFilter(
        field_name='zaaktypes', method=m2m_filter,
        help_text=_('ZAAKTYPE met ZAAKen die relevant kunnen zijn voor dit BESLUITTYPE')
    )
    informatieobjecttypes = filters.CharFilter(
        field_name='informatieobjecttypes', method=m2m_filter,
        help_text=_('Het INFORMATIEOBJECTTYPE van informatieobjecten waarin besluiten van dit '
                    'BESLUITTYPE worden vastgelegd.')
    )
    status = filters.CharFilter(field_name='concept', method=status_filter, help_text=STATUS_HELP_TEXT)

    class Meta:
        model = BesluitType
        fields = (
            'catalogus',
            'zaaktypes',
            'informatieobjecttypes',
            'status'
        )


class CatalogusFilter(FilterSet):
    class Meta:
        model = Catalogus
        fields = {
            'domein': ['exact', 'in'],
            'rsin': ['exact', 'in'],
        }
