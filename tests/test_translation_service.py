import os
import pytest
from frost_harvester.translate import TranslationService
from frost_harvester.models import Thing


@pytest.fixture
def translation_service():
    """Fixture to create TranslationService instance"""
    return TranslationService(os.environ["TRANSLATION_ENDPOINT"])


@pytest.fixture
def sample_thing_json():
    """Fixture providing sample Thing JSON data"""
    return """
    {
      "@iot.selfLink": "https://iot.hamburg.de/v1.1/Things(7648)",
      "@iot.id": 7648,
      "name": "Zählfeld J_52.1_1_I",
      "description": "Zählfeld zur Bestimmung der vom Infrarotdetektor erfassten Fahrräder",
      "properties": {
        "topic": "Transport und Verkehr",
        "assetID": "J_52.1_1_I",
        "keywords": [
          "Infrarotdetektor",
          "Verkehrsmenge",
          "automatisierte Verkehrsmengenerfassung",
          "Hamburger Radzählnetz",
          "Hamburg",
          "aVME",
          "HaRaZäN",
          "Zählfeld"
        ],
        "language": "de",
        "richtung": "Hauptrichtung",
        "ownerThing": "Hamburg Verkehrsanlagen",
        "infoLastUpdate": "2021-10-12T21:07:24.253Z"
      },
      "Datastreams": [
        {
          "@iot.selfLink": "https://iot.hamburg.de/v1.1/Datastreams(16183)",
          "@iot.id": 16183,
          "name": "Fahrradaufkommen an Zählfeld J_52.1_1_I im 5-Min-Intervall",
          "description": "Die Anzahl der von der Infrarotdetektor erfassten Fahrräder wird für ein 5-Min-Intervall aufsummiert.",
          "observationType": "http://defs.opengis.net/elda-common/ogc-def/resource?uri=http://www.opengis.net/def/ogc-om/OM_CountObservation",
          "unitOfMeasurement": {
            "name": "Anzahl",
            "symbol": null,
            "definition": null
          },
          "observedArea": {
            "type": "Point",
            "coordinates": [
              9.978648204,
              53.461316652
            ]
          },
          "phenomenonTime": "2021-10-20T22:00:00Z/2024-12-30T20:34:59Z",
          "properties": {
            "topic": "Verkehr",
            "metadata": "https://registry.gdi-de.org/id/de.hh/292eac0c-b8ab-44ce-a31d-f547ba929d37",
            "layerName": "Anzahl_Fahrraeder_Zaehlfeld_5-Min",
            "ownerData": "Freie und Hansestadt Hamburg",
            "serviceName": "HH_STA_HamburgerRadzaehlnetz",
            "resultNature": "processed",
            "infoLastUpdate": "2023-03-23T13:47:01.843Z",
            "mediaMonitored": "transport"
          },
          "resultTime": "2021-10-21T08:46:04.831Z/2024-12-30T20:37:31.336Z",
          "Sensor": {
            "@iot.selfLink": "https://iot.hamburg.de/v1.1/Sensors(5647)",
            "@iot.id": 5647,
            "name": "Infrarotdetektor in TermiCam2",
            "description": "Infrarotdetektor zur Erfassung von Mobilitätswerkzeugen (u.a. Pkw und Fahrrad)",
            "encodingType": "application/pdf",
            "metadata": "https://flir.netx.net/file/asset/17428/original"
          }
        }
      ],
      "Locations@iot.navigationLink": "https://iot.hamburg.de/v1.1/Things(7648)/Locations",
      "HistoricalLocations@iot.navigationLink": "https://iot.hamburg.de/v1.1/Things(7648)/HistoricalLocations",
      "Datastreams@iot.navigationLink": "https://iot.hamburg.de/v1.1/Things(7648)/Datastreams"
    }   
    """


def test_translate_thing(translation_service, sample_thing_json):
    """Test full Thing translation"""
    # Create Thing object from sample JSON
    thing = Thing.model_validate_json(sample_thing_json)

    # Translate the thing
    translated_thing = translation_service.translate_thing(thing)

    # Assert translations are correct
    assert translated_thing.name != thing.name  # Name should be changed
    # Description should be changed
    assert translated_thing.description != thing.description
    # All keys should be strings
    assert all(isinstance(key, str)
               for key in translated_thing.properties.keys())

    # Check datastream translations
    for ds in translated_thing.datastreams:
        assert isinstance(ds.name, str)
        assert isinstance(ds.description, str)
        if ds.properties:
            assert all(isinstance(key, str) for key in ds.properties.keys())

        # Check sensor translations
        assert isinstance(ds.sensor.name, str)
        assert isinstance(ds.sensor.description, str)


def test_translate_value_string(translation_service):
    """Test translation of simple string value"""
    original = "Verkehr"
    translated = translation_service.translate_value(original)
    assert translated != original
    assert isinstance(translated, str)


def test_translate_value_list(translation_service):
    """Test translation of list values"""
    original = ["Verkehr", "Transport"]
    translated = translation_service.translate_value(original)
    assert all(isinstance(item, str) for item in translated)
    assert translated != original


def test_translate_value_dict(translation_service):
    """Test translation of dictionary values"""
    original = {
        "topic": "Verkehr",
        "type": "Transport"
    }
    translated = translation_service.translate_value(original)
    assert all(isinstance(key, str) for key in translated.keys())
    assert all(isinstance(value, str) for value in translated.values())
    assert translated != original


def test_translate_text(translation_service):
    """Test basic text translation"""
    original = "Verkehr"
    translated = translation_service.translate_text(original)
    assert translated != original
    assert isinstance(translated, str)


def test_empty_properties(translation_service, sample_thing_json):
    """Test handling of empty properties"""
    thing = Thing.model_validate_json(sample_thing_json)
    thing.properties = {}

    translated_thing = translation_service.translate_thing(thing)
    assert translated_thing.properties == {}
