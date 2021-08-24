The purpose of these tools are to transform scraped data (links and content) into pre-labeled samples in tagtog, and to transform post-labeled tagtog data into a readable csv file with labels and metadata. Samples are labelled by annotator, Shammanul Islam, iin the "ikhomyakov/bangladesh_floods" tagtog repository.

To generate the tagtog samples used in this project run "python generateTagtogSamples.py". This requires the appropriate data for sample creation to be located in the data folder. Note that this step is specific to the bangla flood project. For a different project a seperate sample create scheme would have to be created.

To load in tagtog data follow the steps:
1) Downlod the zip file containing annotations and place within the tagtog folder
2) Unzip the annotations folder
3) run "python loadTagTogSamples.py [ANNOTATIONS_FOLDER] [OUTPUT_FILE] [Optional: PRELABELLED_SAMPLE_CSV]"

The output will be a csv containing the samples. Adding PRELABELLED_SAMPLE_CSV will add in any metadata not in the labelled version and add labels to the pre-existing csv.