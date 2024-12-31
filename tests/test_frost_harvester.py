import pytest
import responses
from frost_harvester.harvester.harvester import FrostHarvester
from frost_harvester.harvester.models import Thing


@pytest.fixture
def harvester():
    """Create a FrostHarvester instance for testing"""
    return FrostHarvester("https://test.frost.com/v1.1")


@pytest.fixture
def sample_thing_response():
    """Sample response data from FROST server"""
    return {
        "@iot.count": 2,
        "value": [
            {
                "@iot.selfLink": "https://test.frost.com/v1.1/Things(50)",
                "@iot.id": 50,
                "description": "Test Thing 1",
                "name": "Test Sensor 1",
                "properties": {
                    "status": "active",
                    "type": "test"
                },
                "Datastreams": [
                    {
                        "@iot.id": 100,
                        "name": "Test Datastream 1",
                        "description": "Test Description",
                        "unitOfMeasurement": {
                            "name": "test",
                            "symbol": "t",
                            "definition": "test"
                        },
                        "Sensor": {
                            "@iot.id": 200,
                            "name": "Test Sensor",
                            "description": "Test Sensor Description",
                            "encodingType": "application/pdf"
                        }
                    }
                ]
            },
            {
                "@iot.selfLink": "https://test.frost.com/v1.1/Things(51)",
                "@iot.id": 51,
                "description": "Test Thing 2",
                "name": "Test Sensor 2",
                "properties": {
                    "status": "inactive",
                    "type": "test"
                },
                "Datastreams": []
            }
        ]
    }


@responses.activate
def test_fetch_things_single_page(harvester, sample_thing_response):
    """Test fetching things when there's only one page of results"""
    # Mock the API response
    responses.add(
        responses.GET,
        "https://test.frost.com/v1.1/Things?$expand=Datastreams($expand=Sensor)",
        json=sample_thing_response,
        status=200
    )

    # Fetch things
    things = harvester.fetch_things()
    print(type(things[0]))

    # Verify results
    assert len(things) == 2
    assert isinstance(things[0], Thing)
    assert things[0].id == 50
    assert things[0].name == "Test Sensor 1"
    assert len(things[0].datastreams) == 1
    assert things[1].id == 51
    assert len(things[1].datastreams) == 0


@responses.activate
def test_fetch_things_multiple_pages(harvester, sample_thing_response):
    """Test fetching things with pagination"""
    # First page response
    first_response = sample_thing_response.copy()
    first_response['@iot.nextLink'] = "https://test.frost.com/v1.1/Things?$skip=2"

    # Second page response
    second_response = sample_thing_response.copy()
    second_response['value'] = [
        {
            "@iot.selfLink": "https://test.frost.com/v1.1/Things(52)",
            "@iot.id": 52,
            "description": "Test Thing 3",
            "name": "Test Sensor 3",
            "properties": {"status": "active"},
            "Datastreams": []
        }
    ]

    # Mock the API responses
    responses.add(
        responses.GET,
        "https://test.frost.com/v1.1/Things?$expand=Datastreams($expand=Sensor)",
        json=first_response,
        status=200
    )
    responses.add(
        responses.GET,
        "https://test.frost.com/v1.1/Things?$skip=2",
        json=second_response,
        status=200
    )

    # Fetch things
    things = harvester.fetch_things()

    # Verify results
    assert len(things) == 3
    assert things[2].id == 52


@responses.activate
def test_fetch_things_with_limit(harvester, sample_thing_response):
    """Test fetching things with a limit"""
    responses.add(
        responses.GET,
        "https://test.frost.com/v1.1/Things?$expand=Datastreams($expand=Sensor)",
        json=sample_thing_response,
        status=200
    )

    # Fetch things with limit
    things = harvester.fetch_things(limit=1)

    # Verify results
    assert len(things) == 1
    assert things[0].id == 50


@responses.activate
def test_fetch_things_error_handling(harvester):
    """Test error handling when fetching things"""
    # Mock an error response
    responses.add(
        responses.GET,
        "https://test.frost.com/v1.1/Things?$expand=Datastreams($expand=Sensor)",
        status=500
    )

    # Fetch things
    things = harvester.fetch_things()

    # Verify empty list is returned on error
    assert things == []


def test_base_url_trailing_slash():
    """Test that trailing slashes are handled correctly in base URL"""
    harvester1 = FrostHarvester("https://test.frost.com/v1.1/")
    harvester2 = FrostHarvester("https://test.frost.com/v1.1")

    assert harvester1.base_url == "https://test.frost.com/v1.1"
    assert harvester2.base_url == "https://test.frost.com/v1.1"
