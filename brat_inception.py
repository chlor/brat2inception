import pandas as pd
from cassis import *
from cassis.typesystem import TYPE_NAME_FS_ARRAY, TYPE_NAME_ANNOTATION


#typesystem = TypeSystem()
#neg_fact = typesystem.create_type(name='example.Negation_Faktuality')
#typesystem.create_feature(domainType=neg_fact, name='example', rangeType=TYPE_NAME_ANNOTATION)


#with open('FactCharact_entities_layer.xml', 'rb') as f:
with open('TypeSystem_semant_Ann.xml', 'rb') as f:
    typesystem = load_typesystem(f)

print(typesystem.get_types())

#for t in typesystem.get_types():
#    print(t)




anno_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.ann'
text_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.txt'

plain_text = open(text_file, "r", encoding="utf-8").read()

cas = Cas(
    typesystem=typesystem,
    sofa_string=plain_text,  # Text
    document_language='de'
)

ann = pd.read_csv(anno_file, delimiter='\t', index_col=0, header=None)
ann.columns = ['entity_type_begin_end', 'text']

for index, line in ann.iterrows():
    spl = line['entity_type_begin_end'].split(' ')
    print(spl[0], spl[1], spl[2])

    if ':' not in spl[1]:

        entity_type = spl[0]
        begin = spl[1]
        end = spl[2]

        Token = typesystem.get_type('gemtex.Concept')
        cas.add(
            Token(
                begin=int(begin),
                end=int(end),
                id=spl[0],
                literal=str(spl[0])
            )
        )

cas.to_json('test_data/new_cas.json')
