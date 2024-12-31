import time
import logging
import requests
from typing import List
from frost_harvester.harvester.models import Thing


class FrostHarvester:
    """
    A class to interact with the FROST server and retrieve 'Things' and their associated 'Datastreams'.

    :param base_url: The base URL of the FROST server.
    :type base_url: str
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)

    def fetch_things(self, limit: int = -1) -> List[Thing]:
        """
        Fetches Things along with their Datastreams and Sensors from the FROST server.

        :param limit: The maximum number of Things to fetch.
        :type limit: int
        :return: A list of Thing objects with their associated Datastreams.
        :rtype: List[Thing]
        """
        try:
            # set initial URL to expand Datastreams and Sensors
            url = f"{self.base_url}/Things?$expand=Datastreams($expand=Sensor)"
            things = []
            page_count = 0

            while url:
                self.logger.info("Fetching page %s", page_count + 1)

                response = requests.get(url)
                response.raise_for_status()

                data = response.json()
                if 'value' in data:
                    for idx, value in enumerate(data['value']):
                        # stop if limit is set and reached
                        if idx == limit:
                            return things
                        things.append(Thing.model_validate(value))
                    page_count += 1
                    self.logger.debug(
                        f"Added {len(data['value'])} items from page {page_count}")

                url = data.get('@iot.nextLink')

                if url:
                    time.sleep(0.1)

            return things

        except requests.RequestException as e:
            print(f"Error fetching Things: {e}")
        return []
