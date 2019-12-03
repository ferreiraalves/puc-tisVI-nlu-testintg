import requests
import os
import xmltodict
import json
import untangle
import config
import utils
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

    return response['categories']


def post_cleanup(post):
    aux = post.replace('urlLink','')
    aux = aux.replace('\\', '')
    return aux


def parse_xml(path):
    with open(path, encoding="utf8", errors='replace') as fd:
        read = fd.read().replace('&', '')
        doc = xmltodict.parse(read)
        post_history = ""

        posts_to_read = config.posts
        if len(doc['Blog']['post']) < 10:
            posts_to_read = len(doc['Blog']['post'])

        for i in range(posts_to_read):
            post_history += post_cleanup(doc['Blog']['post'][i])

        return post_history



def evalate_children():
    true_positive = 0
    false_positive = 0
    true_negative = 0
    false_negative = 0
    files = utils.get_files_in_folder('blogs/10s')
    for file in files:
        print(f'Getting file {file}')
        try:
            text = parse_xml(file)
        except xmltodict.expat.ExpatError:
            file_name = file.split('/')[2]
            os.replace(file, f'trash/{file_name}')
        except AttributeError:
            file_name = file.split('/')[2]
            os.replace(file, f'trash/{file_name}')


        #print(f'Getting response for file {file}')
        #categories = get_nlu_reponse(text)
        #print(categories)


def main():

    evalate_children()




if __name__ == '__main__':
    main()
