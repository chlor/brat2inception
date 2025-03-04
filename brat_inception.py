import pandas as pd
from cassis import *
from cassis.typesystem import TYPE_NAME_FS_ARRAY, TYPE_NAME_ANNOTATION


typesystem = TypeSystem()
neg_fact = typesystem.create_type(name='example.Negation_Faktuality')
typesystem.create_feature(domainType=neg_fact, name='example', rangeType=TYPE_NAME_ANNOTATION)
cas = Cas(typesystem=typesystem)

anno_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.ann'
text_file = '/home/chlor/PycharmProjects/brat2inception/test_data/Albers.txt'

plain_text = open(text_file, "r", encoding="utf-8").read()

cas.sofa_string = plain_text

ann = pd.read_csv(anno_file, delimiter='\t', index_col=0, header=None)
ann.columns = ['entity_type_begin_end', 'text']

for index, line in ann.iterrows():
    spl = line['entity_type_begin_end'].split(' ')
    print(spl[0], spl[1], spl[2])

    if ':' not in spl[1]:

        entity_type = spl[0]
        begin = spl[1]
        end = spl[2]

        Annotation = cas.typesystem.get_type(TYPE_NAME_ANNOTATION)
        new_ann = Annotation(begin=int(begin), end=int(end))#, text=line['text'])

        cas.add_annotation(new_ann)

cas.to_json('test_data/new_cas.json')
