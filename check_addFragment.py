import argparse
import configparser
import glob
import os
import sys

import pandas as pd
from cassis import *


def process_brat_file_pair_addFragment(typesystem, text_file, brat_project, outdir):

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

            if ';' in begin or ';' in end:
                print('Add Fragment in ', text_file)
                print(line)
                print(line['entity_type_begin_end'].split(' '))
                print(begin)
                end = spl[len(spl) - 1]
                text = plain_text[int(begin):int(end)]
                print('text')
                print(text)
                print('--------------------------------------')

    splits = text_file.replace(brat_project, outdir).split(os.sep)
    out_file = splits[0] + os.sep + splits[2] + os.sep + splits[1] + '.json'
    cas.to_json(out_file)


def process_project(layer_name, brat_project):

    with open(layer_name, 'rb') as f:
        typesystem = load_typesystem(f)

    outdir = 'out_dir'
    if not os.path.isdir(outdir):
        os.mkdir(outdir)

    annotators = [i for i in os.listdir(brat_project) if i.endswith('.conf') == False]
    for annotator in annotators:
        if not os.path.isdir(outdir + os.sep + annotator):
            os.mkdir(outdir + os.sep + annotator)

    text_files = glob.glob(brat_project + os.sep + '**/*.txt', recursive=True)
    text_files_out = [text_file.replace(brat_project + os.sep + annotators[0] + os.sep, '') for text_file in glob.glob(brat_project + os.sep + annotators[0] + os.sep + '**/*.txt', recursive=True)]

    for t_file in text_files_out:
        if not os.path.isdir(outdir + os.sep + t_file):
            os.mkdir(outdir + os.sep + t_file)

    for text_file in text_files:
        process_brat_file_pair_addFragment(
            text_file=text_file,
            typesystem=typesystem,
            brat_project=brat_project,
            outdir=outdir
        )


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

    brat_project = config['input']['brat_project']
    file_name_typesystem = config['input']['file_name_typesystem']
    process_project(file_name_typesystem, brat_project)
