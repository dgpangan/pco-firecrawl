from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from flasgger import Swagger
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field
from typing import Any, Optional, List

app = Flask(__name__)
api = Api(app)
swagger = Swagger(app)

class NestedModel1(BaseModel):
    title: str
    fulltext_compressed: str
    url: str = None

class ExtractSchema(BaseModel):
    pages: list[NestedModel1]

class ExtractRequestSchema(BaseModel):
    urls: str

class ExtractContent(Resource):
    def post(self):
        """
        This method extracts content from the provided URLs using Firecrawl.
        ---
        tags:
        - Content Extraction
        requestBody:
            required: true
            content:
                application/json:
                    schema:
                        type: object
                        properties:
                            urls:
                                type: string
                                description: Newline-separated URLs to extract content from
                                example: |
                                    https://example.com/page1
                                    https://example.com/page2
                                    https://example.com/page3
        responses:
            200:
                description: Successfully extracted content
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                pages:
                                    type: array
                                    items:
                                        type: object
                                        properties:
                                            title:
                                                type: string
                                                description: The title of the page
                                            fulltext_compressed:
                                                type: string
                                                description: The compressed full text content
                                            url:
                                                type: string
                                                description: The URL of the page
            400:
                description: Invalid request payload
            500:
                description: Extraction failed
        """
        try:
            payload = request.get_json()
            if not payload or 'urls' not in payload:
                return {'error': 'Missing urls in request payload'}, 400

            urls = payload['urls']
            if not isinstance(urls, str):
                return {'error': 'urls must be a string'}, 400

            # Split the string into a list of URLs, removing empty lines and whitespace
            url_list = [url.strip() for url in urls.splitlines() if url.strip()]
            
            if not url_list:
                return {'error': 'No valid URLs provided'}, 400

            app = FirecrawlApp(api_key='fc-cc5558ed7db5423a842ac4f744514257')

            data = app.extract(url_list, {
                'prompt': '',
                'schema': ExtractSchema.model_json_schema(),
            })

            return jsonify(data)
        except Exception as e:
            return {'error': str(e)}, 500

api.add_resource(ExtractContent, "/extract")

if __name__ == "__main__":
    app.run(debug=True)