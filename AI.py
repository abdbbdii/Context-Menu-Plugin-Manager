import json

from google import genai
from google.genai import types
# from pydantic import BaseModel, TypeAdapter


class AI(genai.Client):
    def __init__(self, api_key: str | None = None, schema: dict | None = None, system_instructions: str | None = None):
        self.api_key: str | None = api_key
        self.schema: dict | None = schema
        self.system_instructions: str | None = system_instructions
        self.is_init = False
        self.is_valid = False
        if self.api_key is not None:
            super().__init__(api_key=self.api_key)
            self.is_init = True
    
    def set_api_key(self, api_key: str):
        if not api_key:
            return
        self.api_key = api_key
        super().__init__(api_key=api_key)
        self.is_init = True
        self.is_valid = False

    def get_api_key(self):
        return self.api_key

    def is_key_valid(self):
        if self.is_valid:
            return True
        if not self.is_init or not self.get_api_key():
            return False
        try:
            self.models.list()
            self.is_valid = True
            return True
        except genai.errors.ClientError:
            return False

    def generate_object(self, contents: str):
        if self.schema is None:
            return
        response = self.models.generate_content(
            model="gemini-2.0-flash",
            contents=[self.system_instructions, contents],
            config={
                "response_mime_type": "application/json",
                "response_schema": self.schema,
            },
        )
        return response.parsed

    def generate_content(self, prompt: str):
        response = self.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )
        return response.text

    def generate_images(self, prompt: str, config: dict):
        response = self.models.generate_images(
            model="imagen-3.0-generate-002",
            prompt=prompt,
            config=types.GenerateImagesConfig(
                number_of_images=4,
                **config,
            ),
        )
        # for generated_image in response.generated_images:
        #     image = Image.open(BytesIO(generated_image.image.image_bytes))
        #     image.show()
        return response.generated_images
