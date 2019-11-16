import requests
import os
import json
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions

base_url = 'https://gateway.watsonplatform.net/natural-language-understanding/api'
api_key = os.environ['API_KEY']
model_id = os.environ['MODEL_ID']


def get_nlu_reponse(text):
    authenticator = IAMAuthenticator(f'{api_key}')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2019-07-12',
        authenticator=authenticator,
    )
    natural_language_understanding.set_service_url(f'{base_url}')
    response = natural_language_understanding.analyze(
        text=text,
        features=Features(categories=CategoriesOptions(limit=3, model=model_id))).get_result()

    #TODO: Fix return statement
    print(json.dumps(response, indent=2))


def main():
    get_nlu_reponse("OI")

if __name__ == '__main__':
    main()
