import pandas as pd
from cassis import *


with open('TypeSystem_semant_Ann.xml', 'rb') as f:
    typesystem = load_typesystem(f)

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

    if str(index).startswith('T'):

        entity_type = spl[0]
        begin = spl[1]
        end = spl[2]

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

    if str(index).startswith('R'): #R1	TRUE-ENHANCED Arg1:T12 Arg2:T11
    #    print(index)
    #    print(line)
        print('Dependent', spl[0])
        print('Governor', spl[1].replace('Arg1:', ''))
        print('relations', spl[2].replace('Arg2:', ''))

        def_relation = str(spl[0])
        #def_relation = def_relation.replace('CLIP', 'Clip')
        #def_relation = def_relation.replace('TRUE-ENHANCED', 'True-enhancend')
        #def_relation = def_relation.replace('NEGATED', 'Negated')
        #def_relation = def_relation.replace('UNCERTAIN', 'Uncertain')

    #    print(def_relation)
    #    print('----')

        Rel = typesystem.get_type('gemtex.Relation')

        #print('Rel', Rel)

        #print("str(spl[2].replace('Arg2:', ''))", str(spl[2].replace('Arg2:', '')))
        #print(str(spl[2].replace('Arg2:', ''))[0])

        cas.add(
            Rel(
                Dependent=str(spl[1].replace('Arg1:', '')),
                Governor=str(spl[2].replace('Arg2:', '')),
                kind=def_relation,
            )
        )

#print(cas.get_document_annotation())
#cas.to_json('test_data/new_cas_sem_ann.json')
#relevant_types = [t for t in cas.typesystem.get_types() if 'gemtex' in t.name]
#print(relevant_types)

cas_name = 'gemtex.Concept'  # todo ask

for sentence in cas.select(cas_name):
    for token in cas.select_covered(cas_name, sentence):
        print(token)



# clip\r\nTrue-enhancend\r\nNegated\r\nUncertain\r\nClip",

#clip
#True-enhancend
#Negated
#Uncertain
#Clip",

#TRUE-ENHANCED	Arg1:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE, Arg2:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE
#UNCERTAIN		Arg1:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE, Arg2:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE
#NEGATED			Arg1:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE, Arg2:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE
#CLIP			Arg1:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE, Arg2:TRIGGER|STATEMENT|STATEMENT-NEGATED|ATTRIBUTE
