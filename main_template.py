from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class UppercaseText(Resource):

    def get(self):
        """
        This method responds to the GET request for this endpoint and returns the data in uppercase.
        ---
        tags:
        - Text Processing
        parameters:
            - name: text
              in: query
              type: string
              required: true
              description: The text to be converted to uppercase
        responses:
            200:
                description: A successful GET request
                content:
                    application/json:
                      schema:
                        type: object
                        properties:
                            text:
                                type: string
                                description: The text in uppercase
        """
        text = request.args.get('text')

        return jsonify({"text": text.upper()})

class ExtractSchema(BaseModel):
    title: str
    fulltext_compressed: str

class ExtractContent(Resource):
    def get(self):
        """
        This method extracts content from the Pharmac rules page using Firecrawl.
        ---
        tags:
        - Content Extraction
        responses:
            200:
                description: Successfully extracted content
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                title:
                                    type: string
                                    description: The title of the page
                                fulltext_compressed:
                                    type: string
                                    description: The compressed full text content
            500:
                description: Extraction failed
        """
        app = FirecrawlApp(api_key='fc-cc5558ed7db5423a842ac4f744514257')

        data = app.extract([
        "https://pharmac.govt.nz/pharmaceutical-schedule/general-rules-section-a"
        ], {
            'prompt': '',
            'schema': ExtractSchema.model_json_schema(),
        })

        return jsonify(data)

api.add_resource(UppercaseText, "/uppercase")
api.add_resource(ExtractContent, "/extract")

if __name__ == "__main__":
    app.run(debug=True)