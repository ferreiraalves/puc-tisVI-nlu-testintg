import requests
import os
import xmltodict
import csv
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
#model_id = 'c54eeeb2-9c53-444d-a485-804c5172389a'

adult_folders = ['30s', '40s']

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
    total = 0
    try:
        os.mkdir(f'experiments/{config.experiment_name}')
    except FileExistsError:
        pass

    with open(f'experiments/{config.experiment_name}/child_evaluation.csv', 'w') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(config.csv_header)

        files = utils.get_child_files_in_folder('blogs/10s')
        for idx, file in enumerate(files):
            print(f'[{idx+1}/{len(files)}]Getting file {file}')

            try:
                text = parse_xml(file)
            except xmltodict.expat.ExpatError:
                file_name = file.split('/')[2]
                os.replace(file, f'trash/{file_name}')
            except AttributeError:
                file_name = file.split('/')[2]
                os.replace(file, f'trash/{file_name}')

            print(f'Getting response for file {file}')
            actual_age = file.split('/')[2].split('.')[2]
            try:
                categories = get_nlu_reponse(text)
                predicted_category = categories[0]['label']
                if predicted_category == '/Child':
                    true_positive += 1
                    result = 'true_positive'
                else:
                    false_negative += 1
                    result = 'false_negative'
            except:
                file_name = file.split('/')[2]
                os.replace(file, f'trash/{file_name}')
                result = 'error'
            row = [
                file,
                actual_age,
                'Child',
                predicted_category,
                result
            ]
            writer.writerow(row)
            csvfile.flush()
            total += 1

        for adult_folder in adult_folders:
            files = utils.get_files_in_folder(f'blogs/{adult_folder}')
            for idx, file in enumerate(files):
                print(f'[{idx+1}/{len(files)}]Getting file {file}')

                try:
                    text = parse_xml(file)
                except xmltodict.expat.ExpatError:
                    file_name = file.split('/')[2]
                    os.replace(file, f'trash/{file_name}')
                except AttributeError:
                    file_name = file.split('/')[2]
                    os.replace(file, f'trash/{file_name}')

                print(f'Getting response for file {file}')
                actual_age = file.split('/')[2].split('.')[2]
                try:
                    categories = get_nlu_reponse(text)
                    predicted_category = categories[0]['label']
                    if predicted_category == '/Child':
                        false_positive += 1
                        result = 'false_positive'
                    else:
                        true_negative += 1
                        result = 'true_negative'
                except:
                    file_name = file.split('/')[2]
                    os.replace(file, f'trash/{file_name}')
                    result = 'error'

                row = [
                    file,
                    actual_age,
                    'Adult',
                    predicted_category,
                    result
                ]
                writer.writerow(row)
                csvfile.flush()
                total += 1

    with open(f'experiments/{config.experiment_name}/child_results.txt', 'w') as result_file:
        result_file.write(f'True positives: {true_positive} [{true_positive/total * 100}%]\n')
        result_file.write(f'True negatives: {true_negative} [{true_negative / total * 100}%]\n')
        result_file.write(f'False positives: {false_positive} [{false_positive / total * 100}%]\n')
        result_file.write(f'False negatives: {false_negative} [{false_negative / total * 100}%]\n')
        result_file.write(f'acc: {true_positive + true_negative} [{true_positive + true_negative / total * 100}%]\n')

def main():

    evalate_children()




if __name__ == '__main__':
    main()
