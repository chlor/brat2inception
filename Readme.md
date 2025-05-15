# brat2inception

## Installation

* Install packages from [requirements.txt](requirements.txt):
    ```
    pandas~=2.2.3
    pycaprio~=0.3.0
    dkpro-cassis
    ```
* or run `pip install requirements.txt`

## Preparation

* input: [brat](https://brat.nlplab.org/manual.html) project
* annotations per annotator in one directory
* file structure per annotated document: `file_id.txt` `file_id.ann`, see [brat standoff format](https://brat.nlplab.org/standoff.html)

* check, if you have Add Fragements in your brat project
  * run `python check_addFragment.py`
  * not supported now!! (open issue)
* prepare a UIMA Typesystem, that is compatible with your brat configurations; [example of a generic typesystem](generic_typesystem.xml)
* name of directory name = name of annotator in INCEpTION
* note: annotator names should named by at least 4 characters
* start INCEpTION with remote configuration in `settings.properties`
    ```
    remote-api.enabled=true
    remote-api.http-basic.enabeld=true
    security.default-admin-remote-access=true
    ```
* create user in INCEpTION with the names of the directory path definition
* set an annotation user in INCEpTION with remote role and configure the user data in the following configuration file.


## Configuration

* prepare a configuration file with your parameters in a config file, e.g. [config.conf](config.conf)

* `brat_project` : path of your brat project
* `client_server` : your INCEpTION IP
* `client_user` : user name, e.g. _admin_
* `client_pw` : password of user name
* `new_project_name` : project name of your _new_ INCEpTION project
* `file_name_typesystem` : path of your typesystem
* `layer_name_entities` : definition of your entity layer definition
* `layer_name_relations` : definition of your relation layer definition
* `document_status` : preferred `ANNOTATION_COMPLETE`; allowed: `ANNOTATION_IN_PROGRESS`, `ANNOTATION_COMPLETE`, `CURATION_IN_PROGRESS`, `CURATION_COMPLETE`
* `annotation_status` : preferred `COMPLETE`; allowed: `NEW`, `LOCKED`, `IN_PROGRESS`, `COMPLETE`

* example configuration, see [config.conf](config.conf):
    ```
    [input]
   
    brat_project = data/brat_annotation_data/full
    client_server = http://127.0.0.1:8080
    client_user = admin
    client_pw = admin
    new_project_name = semann-negfakt-7
    file_name_typesystem = full-typesystem.xml
    layer_name_entities = Entity
    layer_name_relations = Relation
    document_status = ANNOTATION_COMPLETE
    annotation_status = COMPLETE 
    ```

## Run

* Run `python create_inception_project_and_insert_documents.py config.conf`
  * creates a new project an inserts the annotation documents into INCEpTION
  * you can also create a new annotation project via INCEpTION: `projects` --> `New Project...`

* Run `python insert_brat_annotation_files_to_inception.py config.conf`
  * insert the annotation into the INCEpTION project

* Update the configuration of the `layers` in INCEpTION with your used typesystem from below

# Note
Add Fragments not supported. It's an open issue.

# Statistics
There is an output of annotation counts of the annotators and all annotations.
It is stored in files `stats_of_annotations.csv` and `stats_of_annotations.xlsx`.

