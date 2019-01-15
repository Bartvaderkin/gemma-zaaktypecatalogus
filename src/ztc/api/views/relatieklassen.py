from rest_framework import viewsets
from zds_schema.viewsets import NestedViewSetMixin

from ...datamodel.models import (
    ZaakInformatieobjectType, ZaakInformatieobjectTypeArchiefregime
)
from ..scopes import SCOPE_ZAAKTYPES_READ
from ..serializers import (
    ZaakInformatieobjectTypeArchiefregimeSerializer,
    ZaakTypeInformatieObjectTypeSerializer
)
from ..utils.rest_flex_fields import FlexFieldsMixin
from ..utils.viewsets import FilterSearchOrderingViewSetMixin


class ZaakTypeInformatieObjectTypeViewSet(NestedViewSetMixin, FilterSearchOrderingViewSetMixin,
                                          FlexFieldsMixin, viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
    Relatie met informatieobjecttype dat relevant is voor zaaktype.

    list:
    Een verzameling van ZAAKINFORMATIEOBJECTTYPEn.
    """
    queryset = ZaakInformatieobjectType.objects.all()
    serializer_class = ZaakTypeInformatieObjectTypeSerializer
    required_scopes = {
        'list': SCOPE_ZAAKTYPES_READ,
        'retrieve': SCOPE_ZAAKTYPES_READ,
    }


class ZaakInformatieobjectTypeArchiefregimeViewSet(NestedViewSetMixin, FilterSearchOrderingViewSetMixin,
                                                   FlexFieldsMixin, viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
    Afwijkende archiveringskenmerken van informatieobjecten van een INFORMATIEOBJECTTYPE bij zaken van een ZAAKTYPE op
    grond van resultaten van een RESULTAATTYPE bij dat ZAAKTYPE.

    list:
    Een verzameling van ZAAKINFORMATIEOBJECTTYPEARCHIEFREGIMEs.
    """
    queryset = ZaakInformatieobjectTypeArchiefregime.objects.all()
    serializer_class = ZaakInformatieobjectTypeArchiefregimeSerializer
    required_scopes = {
        'list': SCOPE_ZAAKTYPES_READ,
        'retrieve': SCOPE_ZAAKTYPES_READ,
    }
