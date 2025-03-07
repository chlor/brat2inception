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

    for index, line in ann.iterrows():

        spl = line['entity_type_begin_end'].split(' ')

        if str(index).startswith('T'):

            entity_type = spl[0]
            begin = spl[1]
            end = spl[2]

            if ';' not in begin and ';' not in end: # Ausschluss von Add-Frag-Elementen todo später

                if layer_name == 'TypeSystem_semant_Ann.xml':
                    Token = typesystem.get_type('gemtex.Concept')
                    #Token = typesystem.get_type('webanno.custom.FactCharact')
                    cas.add(
                        Token(
                            begin=int(begin),
                            end=int(end),
                            #entities=entity_type
                            id=index,
                            literal=entity_type
                        )
                    )
                if layer_name == 'FactRelat_relations_layer.xml':
                    #Token = typesystem.get_type('gemtex.Concept')
                    Token = typesystem.get_type('webanno.custom.FactCharact')
                    cas.add(
                        Token(
                            begin=int(begin),
                            end=int(end),
                            entities=entity_type,
                            #id=index,
                            #literal=entity_type
                        )
                    )

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

brat_project = 'data/full'
#layer_name = 'TypeSystem_semant_Ann.xml'
#process_project_by_layer(layer_name, brat_project)

layer_name = 'FactRelat_relations_layer.xml'
process_project_by_layer(layer_name, brat_project)