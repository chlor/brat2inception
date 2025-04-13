import argparse
import configparser
import sys

from pycaprio import Pycaprio
from pycaprio.mappings import InceptionFormat, DocumentState
import os
import glob


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('conf')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.conf)

    if str(args.conf).startswith('.\\'):
        conf_file = str(args.conf).replace('.\\', '')
    else:
        conf_file = str(args.conf)

    if not os.path.exists(conf_file):
        print('Configuration file not found!')
        sys.exit(1)

    brat_project         = config['input']['brat_project']
    client               = Pycaprio(
                                config['input']['client_server'],
                                authentication=(
                                    config['input']['client_user'],
                                    config['input']['client_pw']
                                )
                            )
    new_project_name     = config['input']['new_project_name']

    document_status = config['input']['document_status']
    if document_status == 'ANNOTATION_IN_PROGRESS':
        document_status = DocumentState.ANNOTATION_IN_PROGRESS
    elif document_status == 'ANNOTATION_COMPLETE':
        document_status = DocumentState.ANNOTATION_COMPLETE
    elif document_status == 'CURATION_IN_PROGRESS':
        document_status = DocumentState.CURATION_IN_PROGRESS
    elif document_status == 'CURATION_COMPLETE':
        document_status = DocumentState.CURATION_COMPLETE
    else:
        document_status = DocumentState.ANNOTATION_COMPLETE

    if new_project_name not in [project.project_name for project in client.api.projects()]:
        print('Create new project named ' + new_project_name)

        new_project = client.api.create_project(new_project_name, creator_name="admin")

        client = Pycaprio(
            config['input']['client_server'],
            authentication=(
                config['input']['client_user'],
                config['input']['client_pw']
            )
        )

        new_project_id = [project.project_id for project in client.api.projects() if project.project_name == new_project_name][0]
    else:
        new_project_id = [project.project_id for project in client.api.projects() if project.project_name == new_project_name][0]
        new_project = client.api.project(new_project_id)
        print('Project ' + new_project_name + ' already exists! No creating of a new project!')

    annotators = [i for i in os.listdir(brat_project) if not i.endswith('.conf')]

    # Get the text documents by files and their names

    text_files = glob.glob(brat_project + os.sep + '**/*.txt', recursive=True)
    text_documents = [(text_file, text_file.replace(brat_project + os.sep + annotators[0] + os.sep, '')) for text_file in glob.glob(brat_project + os.sep + annotators[0] + os.sep + '**/*.txt', recursive=True)]
    documents = {d.document_name: d.document_id for d in client.api.documents(project=new_project_id)}

    # Create the documents in your INCEpTION project

    for text_document_file, text_document_file_name in text_documents:

        if text_document_file_name not in documents.keys():
            with open(text_document_file, 'rb') as document_file:
                new_document = client.api.create_document(
                    new_project_id,
                    text_document_file_name,
                    document_file,
                    document_format=InceptionFormat.TEXT,
                    document_state=document_status
                )
            print(text_document_file_name, 'is inserted a new document.')
        else:
            print(text_document_file_name, 'is inserted already.')
