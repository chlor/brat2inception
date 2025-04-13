import pandas as pd
from cassis import *


#with open('FactCharact_entities_layer.xml', 'rb') as f:
##with open('TypeSystem_semant_Ann.xml', 'rb') as f:
##with open('FactRelat_relations_layer.xml', 'rb') as f:
#    typesystem = load_typesystem(f)

with open('FactRelat_relations_layer.xml', 'rb') as fr:
    typesystem_rel = load_typesystem(fr)


#print(typesystem.get_types())


anno_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.ann'
text_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.txt'

plain_text = open(text_file, "r", encoding="utf-8").read()

cas = Cas(
    typesystem=typesystem_rel,
    sofa_string=plain_text,  # Text
    document_language='de'
)

ann = pd.read_csv(anno_file, delimiter='\t', index_col=0, header=None)
ann.columns = ['entity_type_begin_end', 'text']

for index, line in ann.iterrows():

    spl = line['entity_type_begin_end'].split(' ')
    #print(spl[0], spl[1], spl[2])

    if str(index).startswith('T'):

        entity_type = spl[0]
        begin = spl[1]
        end = spl[2]

        Token = typesystem_rel.get_type('webanno.custom.FactCharact')
        cas.add(
            Token(
                begin=int(begin),
                end=int(end),
                entities=entity_type
            )
        )

    if str(index).startswith('R'):
        print(index)
        print(line)
        print('Dependent', spl[0])
        print('Governor', spl[1].replace('Arg1:', ''))
        print('relations', spl[2].replace('Arg2:', ''))

        def_relation = str(spl[0])
        def_relation = def_relation.replace('CLIP', 'Clip')
        def_relation = def_relation.replace('TRUE-ENHANCED', 'True-enhancend')
        def_relation = def_relation.replace('NEGATED', 'Negated')
        def_relation = def_relation.replace('UNCERTAIN', 'Uncertain')

        print(def_relation)
        print('----')

        Rel = typesystem_rel.get_type('webanno.custom.FactRelat')

        cas.add(
            Rel(
                Dependent=def_relation,
                Governor=str(spl[1].replace('Arg1:', '')),
                relations=str(spl[2].replace('Arg2:', '')),
            )
        )


cas.to_json('test_data/new_cas.json')