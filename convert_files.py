import glob
import os
import pandas as pd
from cassis import *


def process_brat_file_pair(typesystem, text_file, layer_name, brat_project, outdir):
    print(text_file)

    plain_text = open(text_file, "r", encoding="utf-8").read()

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

            if ';' not in begin and ';' not in end: # Ausschluss von Add-Frag-Elementen todo später

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

        if str(index).startswith('R'):  # R1	TRUE-ENHANCED Arg1:T12 Arg2:T11

            def_relation = str(spl[0])
            def_relation = def_relation.replace('CLIP', 'Clip')
            def_relation = def_relation.replace('TRUE-ENHANCED', 'True-enhancend')
            def_relation = def_relation.replace('NEGATED', 'Negated')
            def_relation = def_relation.replace('UNCERTAIN', 'Uncertain')

            node_from = spl[1].replace('Arg1:', '')
            node_to = spl[2].replace('Arg2:', '')

            if layer_name == 'TypeSystem_semant_Ann.xml':
                Rel = typesystem.get_type('gemtex.Relation')
                relation = Rel(
                    Dependent=entities[str(node_from)]['Token'],
                    Governor=entities[str(node_to)]['Token'],
                    kind=def_relation,
                )
                cas.add(relation)

            if layer_name == 'FactRelat_relations_layer.xml':
                Rel = typesystem.get_type('webanno.custom.FactRelat')

                relation = Rel(
                    Dependent=entities[str(node_from)]['Token'],
                    Governor=entities[str(node_to)]['Token'],
                    relations=def_relation,
                )
                cas.add(relation)

    out_file = text_file.replace('.txt', '.json').replace(brat_project, outdir)
    cas.to_json(out_file)
    print(out_file)


def process_project_by_layer(layer_name, brat_project):

    print(process_project_by_layer)
    print('brat_project', brat_project)
    print('layer_name', layer_name)

    with open(layer_name, 'rb') as f:
        typesystem = load_typesystem(f)

    outdir = 'out_dir'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    for annotator in [i for i in os.listdir(brat_project) if i.endswith('.conf') == False]:
        if not os.path.isdir(outdir + os.sep + annotator):
            os.mkdir(outdir + os.sep + annotator)

    #files = [i for i in os.listdir(entry_folder) if i for j in os.listdir(entry_folder) if ".txt" in j in i]
    text_files = glob.glob(brat_project + os.sep + '**/*.txt', recursive=True)

    for text_file in text_files:
        process_brat_file_pair(text_file=text_file, typesystem=typesystem, layer_name=layer_name, brat_project=brat_project, outdir=outdir)


### process test project and uncomment the part below

brat_project = 'data/full'
layer_name = 'TypeSystem_semant_Ann.xml'
process_project_by_layer(layer_name, brat_project)

#layer_name = 'FactRelat_relations_layer.xml'
#process_project_by_layer(layer_name, brat_project)


### process test file and uncomment the part below

with open(layer_name, 'rb') as f:
    typesystem = load_typesystem(f)

outdir = 'out_dir'
text_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.txt'
process_brat_file_pair(typesystem, text_file, layer_name, brat_project, outdir)