import uuid

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, RegexValidator
from django.db import models
from django.utils.translation import ugettext_lazy as _

from zds_schema.fields import (
    DaysDurationField, VertrouwelijkheidsAanduidingField
)

from ..choices import InternExtern, JaNee, ObjectTypen
from .mixins import GeldigheidMixin


class ZaakObjectType(GeldigheidMixin, models.Model):
    """
    De objecttypen van objecten waarop een zaak van het ZAAKTYPE betrekking
    kan hebben.

    Toelichting objecttype
    Een zaak kan op ‘van alles en nog wat’ betrekking hebben.
    Voor zover dit voorkomens (objecten) van de in het RSGB of RGBZ onderscheiden objecttypen
    betreft, wordt met ZAAKOBJECTTYPE gespecificeerd op welke van de RSGB- en/of RGBZ- objecttypen
    zaken van het gerelateerde ZAAKTYPE betrekking kunnen hebben.
    Voor zover het andere objecten betreft, wordt met ZAAKOBJECTTYPE gespecificeerd welke
    andere typen objecten dit betreft.
    """
    # TODO [KING]: objecttype is gespecificeerd als AN40 maar een van de mogelijke waarden
    # (ANDER BUITENLANDS NIET-NATUURLIJK PERSOON) heeft lengte 41. Daarom hebben wij het op max_length=50 gezet
    objecttype = models.CharField(_('objecttype'), max_length=50, help_text=_(
        'De naam van het objecttype waarop zaken van het gerelateerde ZAAKTYPE betrekking hebben.'))
    ander_objecttype = models.CharField(_('ander objecttype'), max_length=1, choices=JaNee.choices, help_text=_(
        'Aanduiding waarmee wordt aangegeven of het ZAAKOBJECTTYPE een ander, niet in RSGB en RGBZ voorkomend, objecttype betreft'))
    relatieomschrijving = models.CharField(_('relatieomschrijving'), max_length=80, help_text=_(
        'Omschrijving van de betrekking van het Objecttype op zaken van het gerelateerde ZAAKTYPE.'))

    status_type = models.ForeignKey(
        'datamodel.StatusType', verbose_name=_('status type'), blank=True, null=True,
        on_delete=models.CASCADE,
        related_name='heeft_verplichte_zaakobjecttype', help_text=_(
            'TODO: dit is de related helptext: De ZAAKOBJECTTYPEn die verplicht gerelateerd moeten zijn aan ZAAKen van '
            'het ZAAKTYPE voordat een STATUS van dit STATUSTYPE kan worden gezet'))

    is_relevant_voor = models.ForeignKey(
        'datamodel.ZaakType', verbose_name=_('is_relevant_voor'), help_text=_(
            'Zaken van het ZAAKTYPE waarvoor objecten van dit ZAAKOBJECTTYPE relevant zijn.'),
        on_delete=models.CASCADE
    )

    class Meta:
        mnemonic = 'ZOT'
        unique_together = ('is_relevant_voor', 'objecttype')
        verbose_name = _('Zaakobjecttype')
        verbose_name_plural = _('Zaakobjecttypen')
        ordering = unique_together

        filter_fields = (
            'is_relevant_voor',
            'ander_objecttype',
        )
        ordering_fields = filter_fields
        search_fields = (
            'objecttype',
            'relatieomschrijving',
        )

    def clean(self):
        """
        Voor het veld objecttype:
        Indien Ander objecttype='N': objecttype moet een van de ObjectTypen zijn
        Indien Ander objecttype='J': alle alfanumerieke tekens

        Datum begin geldigheid:
        - De datum is gelijk aan een Versiedatum van het gerelateerde zaaktype.

        datum einde geldigheid:
        - De datum is gelijk aan of gelegen na de datum zoals opgenomen onder 'Datum begin geldigheid zaakobjecttype’.
        De datum is gelijk aan de dag voor een Versiedatum van het gerelateerde zaaktype.
        """
        super().clean()

        if self.ander_objecttype == JaNee.nee and self.objecttype not in ObjectTypen.values.keys():
            raise ValidationError(_("Indien Ander objecttype='N' moet objecttype een van de objecttypen zijn uit het "
                                    "RSGB of het RGBZ. Bekende objecttypen zijn: {}").format(
                ', '.join(ObjectTypen.values.keys())
            ))

        self._clean_geldigheid(self.is_relevant_voor)

    def __str__(self):
        return '{} - {}{}'.format(self.is_relevant_voor, self.objecttype, self.ander_objecttype)


class ProductDienst(models.Model):
    """
    Het product of de dienst die door ZAAKen van dit ZAAKTYPE
    wordt voortgebracht.

    regels:
    De groepattribuutsoort verandert alleen van waarde
    (materiële historie) cq. één of meer van de subattributen
    veranderen van waarde op een datum die gelijk is aan een
    Versiedatum van het zaaktype.

    Toelichting
    Met deze groepattribuutsoort kan de relatie worden gelegd naar één of meer producten en of
    diensten die met ZAAKen van dit ZAAKTYPE worden geleverd. Omdat aan een product- of
    dienstbeschrijving rechten kunnen worden ontleend, is het van belang dat bij - een versie van -
    een ZAAKTYPE is vastgelegd welke - versie van - een productbeschrijving van toepassing is op
    ZAAKen van dit ZAAKTYPE.
    """
    naam = models.CharField(_('naam'), max_length=80, help_text=_('De naam van het product of de dienst.'))
    link = models.URLField(_('link'), blank=True, null=True, help_text=_(
        'De URL naar de beschrijving van het product of de dienst.'))

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = _('Product / Dienst')
        verbose_name_plural = _('Product / Diensten')


class Formulier(models.Model):
    """
    Het formulier dat ZAAKen van dit ZAAKTYPE initieert.

    Regels
    De groepattribuutsoort verandert alleen van waarde
    (materiële historie) cq. één of meer van de subattributen
    veranderen van waarde op een datum die gelijk is aan een
    Versiedatum van het zaaktype.

    Toelichting
    Met deze groepattribuutsoort wordt de relatie gelegd naar het 'blanco' formulier / de
    formulierdefinitie waarmee ZAAKen van dit ZAAKTYPE worden geïnitieerd. Formulier moet in deze
    context in de ruimste zin van het woord worden opgevat; het kan zowel gaan om het sjabloon
    voor het papieren formulier als het e-formulier dat wordt gebruikt voor de webintake. Om die
    reden is de kardinaliteit 0-N: er kan per kanaal een ander formulier gedefinieerd zijn. De
    kardinaliteit per kanaal is 0-1.
    """
    naam = models.CharField(_('naam'), max_length=80, help_text=_('De naam van het formulier.'))
    link = models.URLField(_('link'), blank=True, null=True, help_text=_('De URL naar het formulier.'))

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = _('Formulier')
        verbose_name_plural = _('Formulieren')


class ReferentieProces(models.Model):
    """
    Het Referentieproces dat ten grondslag ligt aan dit ZAAKTYPE.

    De groepattribuutsoort verandert alleen van waarde
    (materiële historie) cq. één of meer van de subattributen
    veranderen van waarde op een datum die gelijk is aan een
    Versiedatum van het zaaktype.
    """
    naam = models.CharField(_('naam'), max_length=80, help_text=_('De naam van het Referentieproces.'))
    link = models.URLField(_('link'), blank=True, null=True, help_text=_(
        'De URL naar de beschrijving van het Referentieproces'))

    def __str__(self):
        return self.naam

    class Meta:
        verbose_name = _('Referentieprocess')
        verbose_name_plural = _('Referentieprocessen')


class BronCatalogus(models.Model):
    """
    De CATALOGUS waaraan het ZAAKTYPE is ontleend.

    Regels
    De groepattribuutsoort verandert alleen van waarde
    (materiële historie) cq. één of meer van de subattributen
    veranderen van waarde op een datum die gelijk is aan een
    Versiedatum van het zaaktype.

    Toelichting
    Met deze groepattribuutsoort kan een relatie worden gelegd naar de CATALOGUS waaraan de
    configuratie van dit ZAAKTYPE is ontleend. Denk bijvoorbeeld aan het leggen van de relatie tussen
    het 'lokale' ZAAKTYPE 'Aanvraag Uittreksel GBA behandelen' en een specifiek voor de sector
    Burgerzaken ontwikkelde catalogus met alle zaaktypen voor Burgerzaken. De combinatie van deze
    groepattribuutsoort met de attribuutsoort Bronzaaktype-identificatie identificeert het zaaktype
    waarvan dit 'lokale' zaaktype is afgeleid uniek en stelt de beheerder van dit ZAAKTYPE in staat die
    relatie te bewaken.
    """
    domein = models.CharField(_('domein'), max_length=30, help_text=_(
        'Het domein van de CATALOGUS waaraan het ZAAKTYPE is ontleend.'))
    # rsin is gespecificeerd als N9, ivm voorloopnullen gekozen voor CharField. Geen waardenverzameling gedefinieerd
    rsin = models.CharField(_('rsin'), max_length=9, validators=[RegexValidator('^[0-9]*$')], help_text=_(
        'Het RSIN van de INGESCHREVEN NIET-NATUURLIJK PERSOON die beheerder is van de CATALOGUS waaraan het ZAAKTYPE is ontleend.'))

    def __str__(self):
        return '{} - {}'.format(self.rsin, self.domein)

    class Meta:
        verbose_name = _('Bron catalogus')
        verbose_name_plural = _('Bron catalogussen')


class BronZaakType(models.Model):
    """
    Het zaaktype binnen de CATALOGUS waaraan dit ZAAKTYPE is ontleend.

    Regels
    De groepattribuutsoort verandert alleen van waarde
    (materiële historie) cq. één of meer van de subattributen
    veranderen van waarde op een datum die gelijk is aan een
    Versiedatum van het zaaktype.

    Toelichting
    Met de combinatie van deze groepattribuutsoort en de groepattribuutsoort Broncatalogus, kan
    de relatie worden gelegd naar het zaaktype (de bron) dat de basis vormde voor dit ZAAKTYPE.
    Uitgangspunt is dat het zaaktype is afgeleid van de versie van het bronzaaktype zoals dat bestond
    ten tijde van de begindatum van het zaaktype.
    Een voorbeeld is een zaaktype dat is overgenomen uit een landelijk gestandaardiseerde
    CATALOGUS en vervolgens enigszins is aangepast voor toepassing in de eigen organisatie. Door
    het vastleggen van deze relatie kunnen wijzigingen in het bronzaaktype worden gesignaleerd,
    geëvalueerd en mogelijk leiden tot aanpassing van het 'eigen' zaaktype.
    Idealiter is een organisatiespecifiek zaaktypen ontleend aan een referentiecatalogus. Aangezien
    dat vooralsnog niet altijd het geval zal zijn heeft dit groepattribuutsoort de kardinaliteit 0-1.
    Dringend wordt aanbevolen dit groepattribuutsoort wel van waarden te voorzien.
    """
    zaaktype_identificatie = models.PositiveIntegerField(
        _('zaaktype identificatie'), validators=[MaxValueValidator(99999)], help_text=_(
            'De Zaaktype-identificatie van het bronzaaktype binnen de CATALOGUS.'))
    zaaktype_omschrijving = models.CharField(_('zaaktype omschrijving'), max_length=80, help_text=_(
        'De Zaaktype-omschrijving van het bronzaaktype, zoals gehanteerd in de Broncatalogus.'))

    def __str__(self):
        return '{} - {}'.format(self.zaaktype_identificatie, self.zaaktype_omschrijving)

    class Meta:
        verbose_name = _('Bron zaaktype')
        verbose_name_plural = _('Bron zaaktypen')


class ZaakType(GeldigheidMixin, models.Model):
    """
    Het geheel van karakteristieke eigenschappen van zaken van eenzelfde soort

    Toelichting objecttype
    Het betreft de indeling of groepering van zaken naar hun aard, zoals “Behandelen aanvraag
    bouwvergunning” en “Behandelen aanvraag ontheffing parkeren”. Wat in een individueel geval
    een zaak is, waar die begint en waar die eindigt, wordt bekeken vanuit het perspectief van de
    initiator van de zaak (burger, bedrijf, medewerker, etc.). Het traject van (aan)vraag cq.
    aanleiding voor de zaak tot en met de levering van de producten/of diensten die een passend
    antwoord vormen op die aanleiding, bepaalt de omvang en afbakening van de zaak en
    daarmee van het zaaktype. Hiermee komt de afbakening van een zaaktype overeen met een
    bedrijfsproces: ‘van klant tot klant’. Dit betekent ondermeer dat onderdelen van
    bedrijfsprocessen geen zelfstandige zaken vormen. Het betekent ook dat een aanleiding die
    niet leidt tot de start van de uitvoering van een bedrijfsproces, niet leidt tot een zaak (deze
    wordt behandeld in het kader van een reeds lopende zaak).
    Zie ook de toelichtingen bij de relatiesoorten ‘ZAAKTYPE is deelzaaktype van ZAAKTYPE’ en
    ‘ZAAKTYPE heeft gerelateerd ZAAKTYPE’ voor wat betreft zaaktypen van deelzaken
    respectievelijk gerelateerde zaken.
    """
    uuid = models.UUIDField(
        unique=True, default=uuid.uuid4,
        help_text="Unieke resource identifier (UUID4)"
    )
    zaaktype_identificatie = models.PositiveIntegerField(  # N5, integer with max_length of 5
        _('identificatie'), validators=[MaxValueValidator(99999)], help_text=_(
            'Unieke identificatie van het ZAAKTYPE binnen de CATALOGUS waarin het ZAAKTYPE voorkomt.'))
    zaaktype_omschrijving = models.CharField(_('omschrijving'), max_length=80, help_text=_(
        'Omschrijving van de aard van ZAAKen van het ZAAKTYPE.'))
    # TODO [KING]: waardenverzameling zoals vastgelegt in CATALOGUS, wat is deze waardeverzameling dan?
    zaaktype_omschrijving_generiek = models.CharField(
        _('omschrijving generiek'), max_length=80, blank=True, help_text=_(
            'Algemeen gehanteerde omschrijving van de aard van ZAAKen van het ZAAKTYPE'))
    vertrouwelijkheidaanduiding = VertrouwelijkheidsAanduidingField(
        _("vertrouwelijkheidaanduiding"),
        help_text=_("Aanduiding van de mate waarin zaakdossiers van ZAAKen van "
                    "dit ZAAKTYPE voor de openbaarheid bestemd zijn. Indien de zaak bij het "
                    "aanmaken geen vertrouwelijkheidaanduiding krijgt, dan wordt deze waarde gezet.")
    )

    # TODO [KING]: waardenverzameling zie Zaaktypecatalogus, is dat de
    # catalogus die bij dit zaaktype hoort? Wat is de categorie dan?
    # see also: https://github.com/VNG-Realisatie/gemma-zaken/issues/695
    zaakcategorie = models.CharField(
        _("zaakcategorie"), max_length=40, blank=True,
        help_text=_("Typering van de aard van ZAAKen van het ZAAKTYPE.")
    )

    doel = models.TextField(_('doel'), help_text=_(
        'Een omschrijving van hetgeen beoogd is te bereiken met een zaak van dit zaaktype.')
    )
    aanleiding = models.TextField(_('aanleiding'), help_text=_(
        "Een omschrijving van de gebeurtenis die leidt tot het "
        "starten van een ZAAK van dit ZAAKTYPE."
    ))
    toelichting = models.TextField(
        _('toelichting'), blank=True,
        help_text=_('Een eventuele toelichting op dit zaaktype, zoals een beschrijving '
                    'van het procesverloop op de hoofdlijnen.')
    )
    indicatie_intern_of_extern = models.CharField(
        _('indicatie intern of extern'), max_length=6, choices=InternExtern.choices,
        help_text=_('Een aanduiding waarmee onderscheid wordt gemaakt tussen '
                    'ZAAKTYPEn die Intern respectievelijk Extern geïnitieerd worden. '
                    'Indien van beide sprake kan zijn, dan prevaleert de externe initiatie.')
    )
    handeling_initiator = models.CharField(
        _('handeling initiator'), max_length=20,
        help_text=_("Werkwoord dat hoort bij de handeling die de initiator verricht bij dit zaaktype. "
                    "Meestal 'aanvragen', 'indienen' of 'melden'. Zie ook het IOB model op "
                    "https://www.gemmaonline.nl/index.php/Imztc_2.1/doc/attribuutsoort/zaaktype.handeling_initiator")
    )
    onderwerp = models.CharField(
        _('onderwerp'), max_length=80,
        help_text=_("Het onderwerp van ZAAKen van dit ZAAKTYPE. In veel gevallen nauw gerelateerd aan de product- of "
                    "dienstnaam uit de Producten- en Dienstencatalogus (PDC). Bijvoorbeeld: 'Evenementenvergunning', "
                    "'Geboorte', 'Klacht'.")
    )
    handeling_behandelaar = models.CharField(
        _('handeling behandelaar'), max_length=20,
        help_text=_("Werkwoord dat hoort bij de handeling die de behandelaar verricht bij het afdoen van ZAAKen van "
                    "dit ZAAKTYPE. Meestal 'behandelen', 'uitvoeren', 'vaststellen' of 'onderhouden'.")
    )
    doorlooptijd_behandeling = DaysDurationField(
        _('doorlooptijd behandeling'),
        help_text=_('De periode waarbinnen volgens wet- en regelgeving een ZAAK van het ZAAKTYPE '
                    'afgerond dient te zijn, in kalenderdagen.')
    )
    servicenorm_behandeling = DaysDurationField(
        _('servicenorm behandeling'), blank=True, null=True,
        help_text=_('De periode waarbinnen verwacht wordt dat een ZAAK van het ZAAKTYPE afgerond wordt conform '
                    'de geldende servicenormen van de zaakbehandelende organisatie(s).')
    )
    opschorting_aanhouding_mogelijk = models.CharField(
        _('opschorting/aanhouding mogelijk'), max_length=1, choices=JaNee.choices, help_text=_(
            'Aanduiding die aangeeft of ZAAKen van dit mogelijk ZAAKTYPE kunnen worden opgeschort en/of aangehouden.'))
    verlenging_mogelijk = models.CharField(_('verlenging mogelijk'), max_length=1, choices=JaNee.choices, help_text=_(
        'Aanduiding die aangeeft of de Doorlooptijd behandeling van ZAAKen van dit ZAAKTYPE kan worden verlengd.'))
    # TODO [KING]: verlengingstermijn heeft kardinaliteit 1-1 en regel: mag alleen een waarde
    # bevatten als verlenging mogelijk de waarde 'J' heeft
    verlengingstermijn = models.PositiveSmallIntegerField(
        _('verlengingstermijn'), validators=[MaxValueValidator(999)], help_text=_(
            'De termijn in dagen waarmee de Doorlooptijd behandeling van ZAAKen van dit ZAAKTYPE kan worden verlengd.'))
    trefwoord = ArrayField(
        models.CharField(_('trefwoord'), max_length=30),
        blank=True, help_text=_('Een trefwoord waarmee ZAAKen van het ZAAKTYPE kunnen worden '
                                'gekarakteriseerd.(Gebruik een komma om waarden van elkaar te onderscheiden.)'))
    # TODO [KING]: ?? waardenverzameling: De classificatiecode in het gehanteerde
    # archiveringsclassificatiestelsel, gevolgd door een spatie en –
    # tussen haakjes - de gebruikelijke afkorting van de naam van het gehanteerde classificatiestelsel.
    archiefclassificatiecode = models.CharField(
        _('archiefclassificatiecode'), max_length=20, blank=True, null=True, help_text=_(
            'De systematische identificatie van zaakdossiers van dit ZAAKTYPE overeenkomstig logisch gestructureerde '
            'conventies, methoden en procedureregels.'))
    # TODO [KING]: waardenverzameling heeft de volgende regel, momenteel valideren we hier niets,
    # maar wellicht kan het wel: Indien het om een zaaktype in een catalogus voor een specifieke organisatie gaat,
    # dan de naam van een Organisatorische eenheid of Medewerker overeenkomstig het RGBZ.
    # Hoe weten we of een catalogus van een specifieke organisatie is? Als we Catalogus.contactpersoon_beheer_naam
    # gebruiken dan is dit veld overbodig want dan gebruiken we gewoon
    # ZaakType.catalogus.contactpersoon_beheer_naam
    verantwoordelijke = models.CharField(
        _('verantwoordelijke'), max_length=50,
        help_text=_('De (soort) organisatorische eenheid of (functie van) medewerker die verantwoordelijk is voor '
                    'de uitvoering van zaken van het ZAAKTYPE.')
    )
    publicatie_indicatie = models.CharField(
        _('publicatie indicatie'), max_length=1, choices=JaNee.choices,
        help_text=_('Aanduiding of (het starten van) een ZAAK van AN1 dit ZAAKTYPE gepubliceerd moet worden.')
    )
    publicatietekst = models.CharField(_('publicatietekst'), max_length=1000, blank=True, null=True, help_text=_(
        'De generieke tekst van de publicatie van ZAAKen van dit ZAAKTYPE.'))
    verantwoordingsrelatie = ArrayField(
        models.CharField(_('verantwoordingsrelatie'), max_length=40),
        blank=True, help_text=_(
            'De relatie tussen ZAAKen van dit ZAAKTYPE en de beleidsmatige en/of financiële verantwoording. '
            '(Gebruik een komma om waarden van elkaar te onderscheiden.)'))
    versiedatum = models.DateField(_('versiedatum'), help_text=_(
        'De datum waarop de (gewijzigde) kenmerken van het ZAAKTYPE geldig zijn geworden'))

    #
    # groepsattribuutsoorten
    #
    product_dienst = models.ManyToManyField('datamodel.ProductDienst', verbose_name=_('product/dienst'), help_text=_(
        'Het product of de dienst die door ZAAKen van dit ZAAKTYPE wordt voortgebracht.'))
    formulier = models.ManyToManyField(
        'datamodel.Formulier', verbose_name=_('formulier'), blank=True,
        help_text=_('Formulier Het formulier dat ZAAKen van dit ZAAKTYPE initieert.')
    )
    referentieproces = models.ForeignKey(
        'datamodel.ReferentieProces', verbose_name=_('referentieproces'),
        help_text=_('Verwijzing naar een gelijknamig groepattribuutsoort.'),
        on_delete=models.CASCADE
    )
    broncatalogus = models.ForeignKey(
        'datamodel.BronCatalogus', verbose_name=_('broncatalogus'),
        blank=True, null=True, on_delete=models.CASCADE,
        help_text=_('De CATALOGUS waaraan het ZAAKTYPE is ontleend.')
    )
    bronzaaktype = models.ForeignKey(
        'datamodel.BronZaakType', verbose_name=('bronzaaktype'),
        blank=True, null=True, on_delete=models.CASCADE,
        help_text=_('Het zaaktype binnen de CATALOGUS waaraan dit ZAAKTYPE is ontleend.')
    )

    #
    # relaties
    #
    heeft_gerelateerd = models.ManyToManyField(
        'datamodel.ZaakType', verbose_name=_('heeft gerelateerd'), blank=True,
        related_name='zaak_typen_heeft_gerelateerd', through='datamodel.ZaakTypenRelatie',
        help_text=_('De ZAAKTYPEn van zaken die relevant zijn voor zaken van dit ZAAKTYPE.')
    )
    is_deelzaaktype_van = models.ManyToManyField(
        'datamodel.ZaakType', verbose_name=_('is deelzaaktype van'), blank=True,
        related_name='zaak_typen_is_deelzaaktype_van',
        help_text=_('De ZAAKTYPEn (van de hoofdzaken) waaronder ZAAKen van dit ZAAKTYPE als deelzaak kunnen voorkomen.')
    )

    catalogus = models.ForeignKey(
        'datamodel.Catalogus', verbose_name=_('maakt deel uit van'), on_delete=models.CASCADE,
        help_text=_('De CATALOGUS waartoe dit ZAAKTYPE behoort.')
    )

    class Meta:
        mnemonic = 'ZKT'
        unique_together = ('catalogus', 'zaaktype_identificatie')
        verbose_name = _('Zaaktype')
        verbose_name_plural = _('Zaaktypen')
        ordering = unique_together

        filter_fields = (
            'catalogus',
            'publicatie_indicatie',
            'verlenging_mogelijk',
            'opschorting_aanhouding_mogelijk',
            'indicatie_intern_of_extern',
            'vertrouwelijkheidaanduiding',

        )
        ordering_fields = filter_fields
        search_fields = (
            'zaaktype_identificatie',
            'zaaktype_omschrijving',
            'zaaktype_omschrijving_generiek',
            'zaakcategorie',
            'doel',
            'aanleiding',
            'onderwerp',
            'toelichting',
        )

    def __str__(self):
        return '{} - {}'.format(self.catalogus, self.zaaktype_identificatie)

    def clean(self):
        super().clean()

        # self.doorlooptijd_behandeling is empty if there are validation errors,
        # which would trigger a TypeError on the comparison
        if (self.doorlooptijd_behandeling
            and self.servicenorm_behandeling  # noqa
            and self.servicenorm_behandeling > self.doorlooptijd_behandeling):  # noqa
            raise ValidationError("'Servicenorm behandeling' periode mag niet langer zijn dan "
                                  "de periode van 'Doorlooptijd behandeling'.")

        if self.catalogus_id:
            # regel voor zaaktype omschrijving
            if ZaakType.objects.filter(
                catalogus=self.catalogus,
                zaaktype_omschrijving=self.zaaktype_omschrijving
            ).exclude(pk=self.pk).exists():
                raise ValidationError("Zaaktype-omschrijving moet uniek zijn binnen de CATALOGUS.")

        self._clean_geldigheid(self)
