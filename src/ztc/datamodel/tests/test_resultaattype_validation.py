"""
Test the complex validation rules for Resultaattype.

This is tested using the admin-used form class, but can/should be refactored
to validators when using serializer validation.
"""
import uuid
from datetime import timedelta

from django.test import TestCase, tag

import requests_mock
from zds_schema.constants import (
    BrondatumArchiefprocedureAfleidingswijze as Afleidingswijze
)

from ..admin.forms import ResultaatTypeForm
from .factories import ResultaatTypeFactory, ZaakTypeFactory

RESULTAAT_URL = 'https://ref.tst.vng.cloud/referentielijsten/api/v1/resultaten/{uuid}'
PROCESTYPE_URL = 'https://ref.tst.vng.cloud/referentielijsten/api/v1/procestypen/{uuid}'


@tag('resultaattype')
class ResultaattypeSelectielijstlasseValidationTests(TestCase):
    """
    Test the validation on Resultaattype.selectielijstklasse.
    """

    def test_not_a_url(self):
        form = ResultaatTypeForm(data={
            'selectielijstklasse': 'not a url',
        })

        valid = form.is_valid()

        self.assertFalse(valid)
        error = form.errors.as_data()['selectielijstklasse'][0]
        self.assertEqual(error.code, 'invalid')

    def test_404_url(self):
        zaaktype = ZaakTypeFactory.create()
        bad_url = RESULTAAT_URL.format(uuid='5d4b7dac-4452-41b9-ac26-a0c5a1abef9c')
        form = ResultaatTypeForm(data={
            'selectielijstklasse': bad_url,
            'zaaktype': zaaktype.id,
        })

        with requests_mock.Mocker() as m:
            m.register_uri('GET', bad_url, status_code=404)
            valid = form.is_valid()

        self.assertFalse(valid)
        error = form.errors.as_data()['selectielijstklasse'][0]
        self.assertEqual(error.code, 'invalid')

    def test_mismatch_procestype(self):
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)
        bad_resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')

        form = ResultaatTypeForm(data={
            'selectielijstklasse': bad_resultaat_url,
            'zaaktype': zaaktype.id,
        })

        with requests_mock.Mocker() as m:
            m.register_uri('GET', bad_resultaat_url, json={
                'url': bad_resultaat_url,
                # different from zaaktype.selectielijst_procestype
                'procesType': PROCESTYPE_URL.format(uuid='d0176d01-6ba6-407c-aadb-454ee06f4b90')
            })
            valid = form.is_valid()

        self.assertFalse(valid)
        error = form.errors.as_data()['selectielijstklasse'][0]
        self.assertEqual(error.code, 'invalid')

    def test_match_procestype(self):
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)
        good_resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')

        form = ResultaatTypeForm(data={
            'selectielijstklasse': good_resultaat_url,
            'zaaktype': zaaktype.id,
        })

        with requests_mock.Mocker() as m:
            m.register_uri('GET', good_resultaat_url, json={
                'url': good_resultaat_url,
                'procesType': procestype
            })
            form.is_valid()

        self.assertNotIn('selectielijstklasse', form.errors.as_data())


@tag('resultaattype')
class ResultaattypeAfleidingswijzeSelectielijstValidationTests(TestCase):
    """
    Test the validation where afleidingswijze is restricted by the selected selectielijstklasse.
    """

    @requests_mock.Mocker()
    def test_procestermijn_nihil(self, m):
        """
        Validate that the afleidingswijze is fixed for 'nihil' values.

        If the selectielijstresultaat.procestermijn is nihil, then
        afleidingswijze MUST be 'afgehandeld' and vice versa.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)

        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': procestype,
            'procestermijn': 'nihil',
        })

        for value in Afleidingswijze.values:
            if value == Afleidingswijze.afgehandeld:
                continue

            with self.subTest(afleidingswijze=value):
                form = ResultaatTypeForm(data={
                    'selectielijstklasse': resultaat_url,
                    'zaaktype': zaaktype.id,
                    'brondatum_archiefprocedure_afleidingswijze': value
                })

                valid = form.is_valid()

                self.assertFalse(valid)
                error = form.errors.as_data()['brondatum_archiefprocedure_afleidingswijze'][0]
                self.assertEqual(error.code, 'invalid')

    def test_procestermijn_nihil_reverse(self):
        """
        Validate that the afleidingswijze is fixed for 'nihil' values.

        If the selectielijstresultaat.procestermijn is nihil, then
        afleidingswijze MUST be 'afgehandeld' and vice versa.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)

        form = ResultaatTypeForm(data={
            'selectielijstklasse': resultaat_url,
            'zaaktype': zaaktype.id,
            'brondatum_archiefprocedure_afleidingswijze': Afleidingswijze.afgehandeld,
        })

        # See https://ref.tst.vng.cloud/referentielijsten/api/v1/schema/#operation/resultaat_read
        # procesTermijn enum
        for value in (
            'bestaansduur_procesobject',
            'ingeschatte_bestaansduur_procesobject',
            'vast_te_leggen_datum',
            'samengevoegd_met_bewaartermijn',
        ):
            with self.subTest(procestermijn=value):
                with requests_mock.Mocker() as m:
                    # re-use same form instance...
                    form._errors = None

                    # set up selectielijst API mock
                    m.register_uri('GET', resultaat_url, json={
                        'url': resultaat_url,
                        'procesType': procestype,
                        'procestermijn': value,
                    })

                    valid = form.is_valid()

                    self.assertFalse(valid)
                    error = form.errors.as_data()['brondatum_archiefprocedure_afleidingswijze'][0]
                    self.assertEqual(error.code, 'invalid')

    @requests_mock.Mocker()
    def test_procestermijn_ingeschatte_bestaansduur_procesobject(self, m):
        """
        Validate that the afleidingswijze is fixed for 'ingeschatte_bestaansduur_procesobject' values.

        If the selectielijstresultaat.procestermijn is ingeschatte_bestaansduur_procesobject, then
        afleidingswijze MUST be 'afgehandeld' and vice versa.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)

        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': procestype,
            'procestermijn': 'ingeschatte_bestaansduur_procesobject',
        })

        for value in Afleidingswijze.values:
            if value == Afleidingswijze.termijn:
                continue

            with self.subTest(afleidingswijze=value):
                form = ResultaatTypeForm(data={
                    'selectielijstklasse': resultaat_url,
                    'zaaktype': zaaktype.id,
                    'brondatum_archiefprocedure_afleidingswijze': value
                })

                valid = form.is_valid()

                self.assertFalse(valid)
                error = form.errors.as_data()['brondatum_archiefprocedure_afleidingswijze'][0]
                self.assertEqual(error.code, 'invalid')

    def test_procestermijn_ingeschatte_bestaansduur_procesobject_reverse(self):
        """
        Validate that the afleidingswijze is fixed for 'nihil' values.

        If the selectielijstresultaat.procestermijn is nihil, then
        afleidingswijze MUST be 'termijn' and vice versa.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)

        form = ResultaatTypeForm(data={
            'selectielijstklasse': resultaat_url,
            'zaaktype': zaaktype.id,
            'brondatum_archiefprocedure_afleidingswijze': Afleidingswijze.termijn,
        })

        # See https://ref.tst.vng.cloud/referentielijsten/api/v1/schema/#operation/resultaat_read
        # procesTermijn enum
        for value in (
            'nihil',
            'bestaansduur_procesobject',
            'vast_te_leggen_datum',
            'samengevoegd_met_bewaartermijn',
        ):
            with self.subTest(procestermijn=value):
                with requests_mock.Mocker() as m:
                    # re-use same form instance...
                    form._errors = None

                    # set up selectielijst API mock
                    m.register_uri('GET', resultaat_url, json={
                        'url': resultaat_url,
                        'procesType': procestype,
                        'procestermijn': value,
                    })

                    valid = form.is_valid()

                    self.assertFalse(valid)
                    error = form.errors.as_data()['brondatum_archiefprocedure_afleidingswijze'][0]
                    self.assertEqual(error.code, 'invalid')


@tag('resultaattype')
class ResultaattypeAfleidingswijzeAndParameterFieldsValidationTests(TestCase):
    """
    Validate the dependencies between afleidingswijze and paramter fields

    Depending on the chosen afleidingswijze, certain parameter fields are
    required or forbidden.
    """

    def _get_form(self, afleidingswijze: str, zaaktype, resultaat_url: str, **kwargs):
        data = {
            'uuid': str(uuid.uuid4()),
            'selectielijstklasse': resultaat_url,
            'zaaktype': zaaktype.id,
            'omschrijving': 'foobarbaz',
            'omschrijving_generiek': 'https://example.com',
            'datum_begin_geldigheid': zaaktype.versiedatum,
            # 'datum_einde_geldigheid': zaaktype.versiedatum - timedelta(days=1),

            'brondatum_archiefprocedure_afleidingswijze': afleidingswijze,

            # parameter fields - no values allowed!
            'brondatum_archiefprocedure_datumkenmerk': 'foo',
            'brondatum_archiefprocedure_objecttype': 'besluit',  # FIXME - use ZaakObjectTypes
            'brondatum_archiefprocedure_registratie': 'ORC',
        }
        data.update(kwargs)
        return ResultaatTypeForm(data=data)

    def assertParameterFieldsForbidden(self, afleidingswijze: str, procestype: str, resultaat_url: str):
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)
        form = self._get_form(afleidingswijze, zaaktype, resultaat_url)

        valid = form.is_valid()

        self.assertFalse(valid)
        errors = form.errors.as_data()

        self.assertEqual(
            errors['brondatum_archiefprocedure_datumkenmerk'][0].code,
            'invalid'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_objecttype'][0].code,
            'invalid'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_registratie'][0].code,
            'invalid'
        )

    @requests_mock.Mocker()
    def test_only_afleidingswijze_1(self, m):
        """
        Test the values that forbid any parameter fields

        Selected afleidingswijzes do not allow for extra parameters to be
        specified, as they cannot be used by consumers.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')

        ONLY_AFLEIDINGSWIJZE = (
            # Afleidingswijze.afgehandeld,
            Afleidingswijze.gerelateerde_zaak,
            Afleidingswijze.hoofdzaak,
            Afleidingswijze.ingangsdatum_besluit,
            Afleidingswijze.vervaldatum_besluit,
            # Afleidingswijze.termijn,
        )

        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': procestype,
            'procestermijn': 'bestaansduur_procesobject',
        })

        for value in ONLY_AFLEIDINGSWIJZE:
            with self.subTest(afleidingswijze=value):
                self.assertParameterFieldsForbidden(value, procestype, resultaat_url)

    @requests_mock.Mocker()
    def test_only_afleidingswijze_2(self, m):
        """
        Test the values that forbid any parameter fields

        Selected afleidingswijzes do not allow for extra parameters to be
        specified, as they cannot be used by consumers.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')

        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': procestype,
            'procestermijn': 'nihil',
        })

        self.assertParameterFieldsForbidden(Afleidingswijze.afgehandeld, procestype, resultaat_url)

    @requests_mock.Mocker()
    def test_only_afleidingswijze_3(self, m):
        """
        Test the values that forbid any parameter fields

        Selected afleidingswijzes do not allow for extra parameters to be
        specified, as they cannot be used by consumers.
        """
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')

        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': procestype,
            'procestermijn': 'ingeschatte_bestaansduur_procesobject',
        })

        self.assertParameterFieldsForbidden(Afleidingswijze.termijn, procestype, resultaat_url)

    def test_einddatum_bekend_irrelevant(self):
        # For afgehandeld & termijn, the value of the checkbox doesn't matter,
        # so it may not be set to True.
        procestype = PROCESTYPE_URL.format(uuid='e1b73b12-b2f6-4c4e-8929-94f84dd2a57d')
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create(selectielijst_procestype=procestype)

        pairs = (
            ('nihil', Afleidingswijze.afgehandeld),
            ('ingeschatte_bestaansduur_procesobject', Afleidingswijze.termijn),
        )

        for procestermijn, afleidingswijze in pairs:
            with self.subTest(afleidingswijze=afleidingswijze):
                with requests_mock.Mocker() as m:
                    m.register_uri('GET', resultaat_url, json={
                        'url': resultaat_url,
                        'procesType': procestype,
                        'procestermijn': procestermijn,
                    })

                    form = self._get_form(afleidingswijze, zaaktype, resultaat_url, **{
                        'brondatum_archiefprocedure_einddatum_bekend': True
                    })

                    self.assertFalse(form.is_valid())
                    errors = form.errors.as_data()

                    self.assertEqual(
                        errors['brondatum_archiefprocedure_einddatum_bekend'][0].code,
                        'invalid'
                    )

    @requests_mock.Mocker()
    def test_afleidingswijze_eigenschap(self, m):
        """
        Assert that registratie and objecttype are forbidden and datumkenmerk required
        """
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create()
        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': zaaktype.selectielijst_procestype,
            'procestermijn': 'bestaansduur_procesobject',
        })

        form = self._get_form(Afleidingswijze.eigenschap, zaaktype, resultaat_url, **{
            'brondatum_archiefprocedure_datumkenmerk': '',
            'brondatum_archiefprocedure_objecttype': 'besluit',
            'brondatum_archiefprocedure_registratie': 'BRC',
        })

        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()

        self.assertEqual(
            errors['brondatum_archiefprocedure_registratie'][0].code,
            'invalid'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_objecttype'][0].code,
            'invalid'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_datumkenmerk'][0].code,
            'required'
        )

    @requests_mock.Mocker()
    def test_afleidingswijze_zaakobject(self, m):
        """
        Assert that registratie and objecttype are forbidden and datumkenmerk required
        """
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create()
        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': zaaktype.selectielijst_procestype,
            'procestermijn': 'bestaansduur_procesobject',
        })

        form = self._get_form(Afleidingswijze.zaakobject, zaaktype, resultaat_url, **{
            'brondatum_archiefprocedure_datumkenmerk': '',
            'brondatum_archiefprocedure_objecttype': '',
            'brondatum_archiefprocedure_registratie': 'BRC',
        })

        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()

        self.assertEqual(
            errors['brondatum_archiefprocedure_registratie'][0].code,
            'invalid'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_objecttype'][0].code,
            'required'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_datumkenmerk'][0].code,
            'required'
        )

    @requests_mock.Mocker()
    def test_afleidingswijze_ander_datumkenmerk(self, m):
        """
        Assert that registratie and objecttype are forbidden and datumkenmerk required
        """
        resultaat_url = RESULTAAT_URL.format(uuid='ebe82547-609d-464d-875e-7088bf5dc8aa')
        zaaktype = ZaakTypeFactory.create()
        # set up selectielijst API mock
        m.register_uri('GET', resultaat_url, json={
            'url': resultaat_url,
            'procesType': zaaktype.selectielijst_procestype,
            'procestermijn': 'bestaansduur_procesobject',
        })

        form = self._get_form(Afleidingswijze.ander_datumkenmerk, zaaktype, resultaat_url, **{
            'brondatum_archiefprocedure_datumkenmerk': '',
            'brondatum_archiefprocedure_objecttype': '',
            'brondatum_archiefprocedure_registratie': '',
        })

        self.assertFalse(form.is_valid())
        errors = form.errors.as_data()

        self.assertEqual(
            errors['brondatum_archiefprocedure_registratie'][0].code,
            'required'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_objecttype'][0].code,
            'required'
        )
        self.assertEqual(
            errors['brondatum_archiefprocedure_datumkenmerk'][0].code,
            'required'
        )
