import argparse
import configparser
import sys
from cassis import *
from pycaprio import Pycaprio
from pycaprio.mappings import InceptionFormat, AnnotationState, DocumentState
import os
import pandas as pd
import glob


def process_brat_file_pair(typesystem, text_file, layer_name_entities, layer_name_relations):

    plain_text = open(text_file, "r", encoding="utf-8").read()

    if plain_text[0].encode("utf-8") == b'\xef\xbb\xbf':
        print("Warning:", text_file, "starts with 'Byte Order Mark'. It is removed.")
        shift = True
        plain_text = plain_text[1:]
    else:
        shift = False

    cas = Cas(
        typesystem=typesystem,
        sofa_string=plain_text,
        document_language='de'
    )
    anno_file = text_file.replace('.txt', '.ann')
    ann = pd.read_csv(anno_file, delimiter='\t', index_col=0, header=None)
    ann.columns = ['entity_type_begin_end', 'text']

    entities = {}

    for index, line in ann.iterrows():

        spl = line['entity_type_begin_end'].split(' ')

        if str(index).startswith('T'):

            entity_type = spl[0]#.split('\ţ')[1]
            begin = spl[1]
            end = spl[2]

            entities[str(index)] = {'entity_type': entity_type}

            if not (';' not in begin and ';' not in end):
                end = spl[len(spl) - 1]

            Token = typesystem.get_type(layer_name_entities)  # 'gemtex.Concept'

            if not shift:
                new_token = Token(
                        begin=int(begin),
                        end=int(end),
                        id=entity_type,
                        #literal=entity_type  # use it for attributions later, it's renamed to attribute
                    )
            else:
                new_token = Token(
                        begin=int(begin) - 1,
                        end=int(end) - 1,
                        id=entity_type,
                        #literal=entity_type  # use it for attributions later, it's renamed to attribute
                    )

            entities[str(index)]['Token'] = new_token
            cas.add(new_token)

        if str(index).startswith('R'):  # R1	TRUE-ENHANCED Arg1:T12 Arg2:T11

            def_relation = str(spl[0])
            def_relation = def_relation.replace('CLIP', 'Clip')
            def_relation = def_relation.replace('TRUE-ENHANCED', 'True-enhancend')
            def_relation = def_relation.replace('NEGATED', 'Negated')
            def_relation = def_relation.replace('UNCERTAIN', 'Uncertain')

            node_from = spl[1].replace('Arg1:', '')
            node_to = spl[2].replace('Arg2:', '')

            Rel = typesystem.get_type(layer_name_relations)
            relation = Rel(
                Dependent=entities[str(node_from)]['Token'],
                Governor=entities[str(node_to)]['Token'],
                kind=def_relation,
                begin=entities[str(node_from)]['Token']['begin'],
                end=entities[str(node_from)]['Token']['end']
            )

            cas.add(relation)

    xmi_file_cas = text_file.replace('.txt', '.xml')
    cas.to_xmi(xmi_file_cas)

    return entities, xmi_file_cas


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
    file_name_typesystem = config['input']['file_name_typesystem']
    layer_name_entities  = config['input']['layer_name_entities']
    layer_name_relations = config['input']['layer_name_relations']

    document_status      = config['input']['document_status']

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

    annotation_status    = config['input']['annotation_status']

    if annotation_status == 'NEW':
        annotation_status = AnnotationState.NEW
    elif annotation_status == 'LOCKED':
        annotation_status = AnnotationState.LOCKED
    elif annotation_status == 'IN_PROGRESS':
        annotation_status = AnnotationState.IN_PROGRESS
    elif annotation_status == 'COMPLETE':
        annotation_status = AnnotationState.COMPLETE
    else:
        annotation_status = AnnotationState.COMPLETE

    # Check if project exists

    if new_project_name not in [project.project_name for project in client.api.projects()]:
        print("Project named '" + new_project_name + "' not found!")
        print("Run 'create_inception_project_and_insert_documents.py config.conf'!")
        exit(1)
    else:
        new_project_id = [project.project_id for project in client.api.projects() if project.project_name == new_project_name][0]
        new_project = client.api.project(new_project_id)
        print('Project ' + new_project_name + ' is loaded.')

    # Get the names of the annotators

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
        else:
            print(text_document_file_name, 'is inserted already.')

    annotated_documents = {
        ann: [(text_file, text_file.replace(brat_project + os.sep + annotators[i] + os.sep, ''))
                for text_file in glob.glob(brat_project + os.sep + annotators[i] + os.sep + '**/*.txt', recursive=True)] for i,ann in enumerate(annotators)
    }

    # Load the Typesystem

    with open(file_name_typesystem, 'rb') as fr:
        typesystem = load_typesystem(fr)

    # Insert the annotations from brat in INCEpTION

    list_not_inserted = []

    annotated_entities = {}

    for annotator in annotated_documents:

        for text_document_file, text_document_file_name in annotated_documents[annotator]:

            ann_file = text_document_file.replace('.txt', '.ann')

            #annotated_entities[(annotator, text_document_file_name)], file_with_cas = process_brat_file_pair(
            annotated_ents, file_with_cas = process_brat_file_pair(
                text_file=text_document_file,
                typesystem=typesystem,
                layer_name_entities=layer_name_entities,
                layer_name_relations=layer_name_relations
            )

            df_ents = pd.DataFrame(annotated_ents).transpose()
            #print(df_ents['entity_type'] == 'STATEMENT')
            #print(df_ents['entity_type'] == 'TRIGGER')
            #print(df_ents['entity_type'])
            #print(df_ents['entity_type'].value_counts())
            annotated_entities[text_document_file_name, annotator] = dict(df_ents['entity_type'].value_counts())

            try:
                with open(file_with_cas, 'rb') as annotation_file:
                    new_annotation = client.api.create_annotation(
                        project=new_project_id,
                        document=documents[text_document_file_name],
                        user_name=annotator,
                        content=annotation_file,
                        annotation_format="xmi",
                        annotation_state=annotation_status
                    )

                    print(
                        'project', new_project_id,
                        'document', documents[text_document_file_name],
                        'user_name', annotator,
                        'content', text_document_file,
                        'annotation_format', "xmi",
                        'annotation_state', annotation_status, 'is insersted.'
                    )
            except:
                print(text_document_file, 'is not inserted.')
                list_not_inserted.append(text_document_file)

    df_result = pd.DataFrame(annotated_entities).transpose().reset_index()
    df_result.to_csv('stats_of_annotations.csv')
    df_result.to_excel('stats_of_annotations.xlsx')

    # Filter über alle Annotatoren in 'level_1' und dann Summenbildung

    for annotator in annotators:
        print(annotator)
        print(df_result.loc[df_result['level_1'] == annotator].sum())

    if not list_not_inserted:
        print('All documents inserted!')
    else:
        print(len(list_not_inserted), 'documents that are not inserted:')

        print(list_not_inserted)
