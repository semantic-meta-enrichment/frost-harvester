import requests
from frost_harvester.models import Thing


class TranslationService:
    def __init__(self, url: str):
        self.url = url
        self.headers = {"Content-Type": "application/json"}

    def translate_thing(self, translated_thing: Thing):

        translated_thing = translated_thing.model_copy(deep=True)

        translated_thing.name = self.translate_text(translated_thing.name)
        translated_thing.description = self.translate_text(
            translated_thing.description)

        if translated_thing.properties:
            translated_props = {}
            for k, v in translated_thing.properties.items():
                translated_key = self.translate_text(k)
                translated_value = self.translate_value(v)
                translated_props[translated_key] = translated_value

            translated_thing.properties = translated_props

        for idx, ds in enumerate(translated_thing.datastreams):

            updated_sensor = ds.sensor.model_copy(update={
                'name': self.translate_text(ds.sensor.name),
                'description': self.translate_text(ds.sensor.description)
                # other sensor fields to update
            })
            updated_ds = ds.model_copy(update={
                'name': self.translate_text(ds.name),
                'description': self.translate_text(ds.description),
                'unitOfMeasurement': self.translate_value(ds.unit_of_measurement),
                'properties': self.translate_value(ds.properties) if ds.properties else None,
                'sensor': updated_sensor

            })

            translated_thing.datastreams[idx] = updated_ds

        return translated_thing

    def translate_value(self, value):
        """Recursively translate values that are strings or lists"""
        if isinstance(value, str):
            print(self.translate_text(value))
            return self.translate_text(value)
        elif isinstance(value, list):
            return [self.translate_value(item) for item in value]
        elif isinstance(value, dict):
            return {self.translate_text(k): self.translate_value(v) for k, v in value.items()}
        return value

    def translate_text(self, text: str):
        payload = {
            "q": text,
            "source": "de",
            "target": "en"
        }

        response = requests.post(
            f"{self.url}/translate", json=payload, headers=self.headers)
        return response.json()["translatedText"]
