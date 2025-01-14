from rest_framework import mixins, viewsets
from vng_api_common.notifications.viewsets import (
    NotificationCreateMixin, NotificationDestroyMixin
)

from ...datamodel.models import BesluitType
from ..filters import BesluitTypeFilter
from ..kanalen import KANAAL_BESLUITTYPEN
from ..scopes import SCOPE_ZAAKTYPES_READ, SCOPE_ZAAKTYPES_WRITE
from ..serializers import BesluitTypeSerializer
from .mixins import ConceptMixin, M2MConceptCreateMixin


class BesluitTypeViewSet(ConceptMixin,
                         M2MConceptCreateMixin,
                         NotificationCreateMixin,
                         NotificationDestroyMixin,
                         mixins.CreateModelMixin,
                         mixins.DestroyModelMixin,
                         viewsets.ReadOnlyModelViewSet):
    """
    Opvragen en bewerken van BESLUITTYPEn nodig voor BESLUITEN in de Besluiten
    API.

    Alle BESLUITTYPEn van de besluiten die het resultaat kunnen zijn van het
    zaakgericht werken van de behandelende organisatie(s).

    create:
    Maak een BESLUITTYPE aan.

    Maak een BESLUITTYPE aan.

    list:
    Alle BESLUITTYPEn opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke BESLUITTYPE opvragen.

    Een specifieke BESLUITTYPE opvragen.

    update:
    Werk een BESLUITTYPE in zijn geheel bij.

    Werk een BESLUITTYPE in zijn geheel bij. Dit kan alleen als het een concept
    betreft.

    partial_update:
    Werk een BESLUITTYPE deels bij.

    Werk een BESLUITTYPE deels bij. Dit kan alleen als het een concept betreft.

    destroy:
    Verwijder een BESLUITTYPE.

    Verwijder een BESLUITTYPE. Dit kan alleen als het een concept betreft.
    """
    queryset = BesluitType.objects.all().order_by('-pk')
    serializer_class = BesluitTypeSerializer
    filterset_class = BesluitTypeFilter
    lookup_field = 'uuid'
    required_scopes = {
        'list': SCOPE_ZAAKTYPES_READ,
        'retrieve': SCOPE_ZAAKTYPES_READ,
        'create': SCOPE_ZAAKTYPES_WRITE,
        'destroy': SCOPE_ZAAKTYPES_WRITE,
        'publish': SCOPE_ZAAKTYPES_WRITE,
    }
    concept_related_fields = ['informatieobjecttypes', 'zaaktypes']
    notifications_kanaal = KANAAL_BESLUITTYPEN
