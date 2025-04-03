from pycaprio import Pycaprio
from pycaprio.mappings import InceptionFormat, DocumentState
from pycaprio.mappings import InceptionFormat, AnnotationState
import os
import pandas as pd
from cassis import *
import glob


def process_brat_file_pair(typesystem, text_file, layer_name):

    plain_text = open(text_file, "r", encoding="utf-8").read()

    # 1) create a document if not exists
    # 2) create a Cas if not exists

    cas = Cas(
        typesystem=typesystem,
        sofa_string=plain_text,  # Text
        document_language='de'
    )
    anno_file = text_file.replace('.txt', '.ann')
    ann = pd.read_csv(anno_file, delimiter='\t', index_col=0, header=None)
    ann.columns = ['entity_type_begin_end', 'text']

    entities = {}

    for index, line in ann.iterrows():

        spl = line['entity_type_begin_end'].split(' ')

        if str(index).startswith('T'):

            entity_type = spl[0]
            begin = spl[1]
            end = spl[2]

            entities[str(index)] = {'entity_type': entity_type, 'begin': begin, 'end': end}

            if not (';' not in begin and ';' not in end):
                end = spl[len(spl) - 1]

            if layer_name == 'TypeSystem_semant_Ann.xml':
                Token = typesystem.get_type('gemtex.Concept')

                new_token = Token(
                        begin=int(begin),
                        end=int(end),
                        id=index,
                        literal=entity_type
                    )
                entities[str(index)]['Token'] = new_token
                cas.add(new_token)
            if layer_name == 'FactRelat_relations_layer.xml':
                Token = typesystem.get_type('webanno.custom.FactRelat')
                new_token = Token(
                    begin=int(begin),
                    end=int(end),
                    entities=entity_type,
                )

                cas.add(new_token)
                entities[str(index)]['Token'] = new_token
                cas.add(new_token)


    #splits = text_file.replace(brat_project, outdir).split(os.sep)

    #out_file = text_file.replace('.txt', '.json').replace(brat_project, outdir)
    #out_file = splits[0] + os.sep + splits[2] + os.sep + splits[1] + '.json'

    xmi_file_cas = text_file.replace('.txt', '.xml')
    cas.to_xmi(xmi_file_cas)
    #print(out_file)
    #out_file_xml = splits[0] + os.sep + splits[2] + os.sep + splits[1] + '.xmi'
    #cas.to_xmi(out_file_xml)
    #print(out_file_xml)

    #print('Check Sofa ', text_file)
    #print(cas.sofa_string[0], cas.sofa_string[1], cas.sofa_string[2], cas.sofa_string[3])
    #print(cas.sofa_string[0])
    #print(cas.sofa_string[0].encode("utf-8"))
    #print(cas.sofa_string[0].decode("utf-8"))
    #print('~~~~~~~~~~')

    return xmi_file_cas

brat_project = 'data/full'
client = Pycaprio("http://127.0.0.1:8080", authentication=("admin", "admin"))
new_project_name = 'semann-negfakt-3'
projects = client.api.projects()
if new_project_name not in [project.project_name for project in projects]:
    new_project = client.api.create_project(new_project_name, creator_name="admin")
else:
    new_project_id = [project.project_id for project in projects if project.project_name == new_project_name][0]
    new_project = client.api.project(new_project_id)


annotators = [i for i in os.listdir(brat_project) if not i.endswith('.conf')]

text_files = glob.glob(brat_project + os.sep + '**/*.txt', recursive=True)
text_documents = [(text_file, text_file.replace(brat_project + os.sep + annotators[0] + os.sep, '')) for text_file in glob.glob(brat_project + os.sep + annotators[0] + os.sep + '**/*.txt', recursive=True)]

#document_names = [d.document_name for d in client.api.documents(project=new_project_id)]
documents = {d.document_name: d.document_id for d in client.api.documents(project=new_project_id)}

for text_document_file, text_document_file_name in text_documents:
    if text_document_file_name not in documents.keys():

        #open(text_file, "r", encoding="utf-8").read()
        with open(text_document_file, 'rb') as document_file:
            new_document = client.api.create_document(
                new_project_id,
                text_document_file_name,
                document_file,
                document_format=InceptionFormat.TEXT#, document_state=DocumentState.ANNOTATION_COMPLETE
            )
    else:
        print(text_document_file_name, 'is inserted.')


print(annotators)

annotated_documents = {ann: [(text_file, text_file.replace(brat_project + os.sep + annotators[i] + os.sep, '')) for text_file in glob.glob(brat_project + os.sep + annotators[i] + os.sep + '**/*.txt', recursive=True)] for i,ann in enumerate(annotators)}

print(annotated_documents)

with open('TypeSystem_semant_Ann.xml', 'rb') as fr:
    typesystem = load_typesystem(fr)

list_not_inserted = []

for annotator in annotated_documents:
    for text_document_file, text_document_file_name in annotated_documents[annotator]:

        ann_file = text_document_file.replace('.txt', '.ann')

        file_with_cas = process_brat_file_pair(
            text_file=text_document_file,
            typesystem=typesystem,
            layer_name='TypeSystem_semant_Ann.xml'
        )

        ann_intern = annotator.replace('dal', 'annotator_1').replace('fritzsch', 'annotator_2').replace('rudolphi', 'annotator_3')

        print(
            'project', new_project_id,
            'document', documents[text_document_file_name],
            'user_name', ann_intern,
            'content', text_document_file,
            'annotation_format', "xmi",
            'annotation_state', AnnotationState.IN_PROGRESS
        )

        try:
            with open(file_with_cas, 'rb') as annotation_file:
                new_annotation = client.api.create_annotation(
                    project=new_project_id,
                    document=documents[text_document_file_name],
                    user_name=ann_intern,
                    content=annotation_file,
                    annotation_format="xmi",
                    annotation_state=AnnotationState.IN_PROGRESS
                )
        except:
            print(text_document_file, 'is not inserted.')
            list_not_inserted.append(text_document_file)

print('documents that are not inserted:')
print(list_not_inserted)
