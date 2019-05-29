from rest_framework import viewsets
from vng_api_common.viewsets import CheckQueryParamsMixin, NestedViewSetMixin

from ..filters import RolTypeFilter
from ..scopes import SCOPE_ZAAKTYPES_READ
from ..serializers import RolTypeSerializer
from ...datamodel.models import RolType


class RolTypeViewSet(CheckQueryParamsMixin, NestedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    """
    retrieve:
    Generieke aanduiding van de aard van een ROL die een BETROKKENE kan uitoefenen in ZAAKen van een ZAAKTYPE.

    list:
    Een verzameling van ROLTYPEn.
    """
    queryset = RolType.objects.prefetch_related('mogelijkebetrokkene_set')
    serializer_class = RolTypeSerializer
    filterset_class = RolTypeFilter
    pagination_class = None
    lookup_field = 'uuid'
    required_scopes = {
        'list': SCOPE_ZAAKTYPES_READ,
        'retrieve': SCOPE_ZAAKTYPES_READ,
    }
