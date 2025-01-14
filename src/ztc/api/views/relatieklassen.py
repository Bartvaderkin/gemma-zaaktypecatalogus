from django.utils.translation import ugettext_lazy as _

from rest_framework import mixins, viewsets
from rest_framework.exceptions import PermissionDenied

from ...datamodel.models import ZaakInformatieobjectType
from ..filters import ZaakInformatieobjectTypeFilter
from ..scopes import SCOPE_ZAAKTYPES_READ, SCOPE_ZAAKTYPES_WRITE
from ..serializers import ZaakTypeInformatieObjectTypeSerializer
from .mixins import ConceptDestroyMixin, ConceptFilterMixin


class ZaakTypeInformatieObjectTypeViewSet(ConceptFilterMixin,
                                          ConceptDestroyMixin,
                                          mixins.CreateModelMixin,
                                          mixins.DestroyModelMixin,
                                          viewsets.ReadOnlyModelViewSet):
    """
    Opvragen en bewerken van ZAAKTYPE-INFORMATIEOBJECTTYPE relaties.

    Geeft aan welke INFORMATIEOBJECTTYPEn binnen een ZAAKTYPE mogelijk zijn en
    hoe de richting is.

    create:
    Maak een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie aan.

    Maak een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie aan. Dit kan alleen als het
    bijbehorende ZAAKTYPE een concept betreft.

    list:
    Alle ZAAKTYPE-INFORMATIEOBJECTTYPE relaties opvragen.

    Deze lijst kan gefilterd wordt met query-string parameters.

    retrieve:
    Een specifieke ZAAKTYPE-INFORMATIEOBJECTTYPE relatie opvragen.

    Een specifieke ZAAKTYPE-INFORMATIEOBJECTTYPE relatie opvragen.

    update:
    Werk een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie in zijn geheel bij.

    Werk een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie in zijn geheel bij. Dit kan
    alleen als het bijbehorende ZAAKTYPE een concept betreft.

    partial_update:
    Werk een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie deels bij.

    Werk een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie deels bij. Dit kan alleen
    als het bijbehorende ZAAKTYPE een concept betreft.

    destroy:
    Verwijder een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie.

    Verwijder een ZAAKTYPE-INFORMATIEOBJECTTYPE relatie. Dit kan alleen als
    het bijbehorende ZAAKTYPE een concept betreft.
    """
    queryset = ZaakInformatieobjectType.objects.all().order_by('-pk')
    serializer_class = ZaakTypeInformatieObjectTypeSerializer
    filterset_class = ZaakInformatieobjectTypeFilter
    lookup_field = 'uuid'
    required_scopes = {
        'list': SCOPE_ZAAKTYPES_READ,
        'retrieve': SCOPE_ZAAKTYPES_READ,
        'create': SCOPE_ZAAKTYPES_WRITE,
        'destroy': SCOPE_ZAAKTYPES_WRITE,
    }

    def get_concept(self, instance):
        return instance.zaaktype.concept and instance.informatieobjecttype.concept

    def perform_create(self, serializer):
        zaaktype = serializer.validated_data['zaaktype']
        informatieobjecttype = serializer.validated_data['informatieobjecttype']

        if not(zaaktype.concept and informatieobjecttype.concept):
            msg = _("Creating relations between non-concept objects is forbidden")
            raise PermissionDenied(detail=msg)
        super().perform_create(serializer)

    def get_concept_filter(self):
        return {'zaaktype__concept': False, 'informatieobjecttype__concept': False}


# class ZaakInformatieobjectTypeArchiefregimeViewSet(NestedViewSetMixin, FilterSearchOrderingViewSetMixin,
#                                                    FlexFieldsMixin, viewsets.ReadOnlyModelViewSet):
#     """
#     retrieve:
#     Afwijkende archiveringskenmerken van informatieobjecten van een INFORMATIEOBJECTTYPE bij zaken van een ZAAKTYPE op
#     grond van resultaten van een RESULTAATTYPE bij dat ZAAKTYPE.
#
#     list:
#     Een verzameling van ZAAKINFORMATIEOBJECTTYPEARCHIEFREGIMEs.
#     """
#     queryset = ZaakInformatieobjectTypeArchiefregime.objects.all()
#     serializer_class = ZaakInformatieobjectTypeArchiefregimeSerializer
#     required_scopes = {
#         'list': SCOPE_ZAAKTYPES_READ,
#         'retrieve': SCOPE_ZAAKTYPES_READ,
#     }
