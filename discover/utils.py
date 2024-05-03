import os
import io
import glob
import pandas as pd
import tempfile
import pm4py
import json
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator

from pm4py.objects.conversion.log.variants import to_event_log

from zipfile import ZipFile
from .models.qual_params import QualityResult


async def read_csv(file):

    dataframe = pd.read_csv(file, sep=";")

    # renaming the col ending with _id
    dataframe.rename(columns=lambda x: 'case:concept:name' if x.endswith('_id') else x, inplace=True)
    dataframe.rename(columns=lambda x: 'time:timestamp' if x.endswith('timestamp') else x, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)

    # Convert timestamp column to datetime and handle mixed format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format='mixed')

    dataframe = pm4py.format_dataframe(dataframe, case_id='case:concept:name', activity_key='concept:name',
                                       timestamp_key='time:timestamp')

    log = to_event_log.apply(dataframe)

    return log

async def read_files(file_path):
    # read the log files depending on its extension
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        log = await read_csv(file_path)
        return log
    elif extension == '.xes':
        log = pm4py.read_xes(file_path)
        return log


def latest_image():
    # get the path of the latest image stored in temp files

    tmp_dir = os.path.expanduser('/temp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image


def generate_zip(diagram_path, pnml_path, qual_path):

    # create a zip file containing the png of the model, its quality and the pnml file
    zip_path = "src/temp/Zipped_file.zip"
    with ZipFile(zip_path, 'w') as zip_object:
        # Adding files that need to be zipped
        zip_object.write(pnml_path,arcname='pnml_file.pnml')

        name_png = os.path.split(diagram_path)

        zip_object.write(diagram_path, arcname = name_png[1])
        zip_object.write(qual_path, arcname="algo_quality.json")

    # Remove the files from temp folder
    os.remove(diagram_path)
    os.remove(pnml_path)
    os.remove(qual_path)

    # Check to see if the zip file is created
    if os.path.exists(zip_path):
        return "ZIP file created :", zip_path
    else:
        return "ZIP file not created"


def calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach):
    generalization = generalization_evaluator.apply(log, net, initial_marking, final_marking)
    if fitness_approach == "token based":
        fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking)
    else:
        fitness = pm4py.fitness_alignments(log, net, initial_marking, final_marking)
    if precision_approach == "token based":
        precision = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking)
    else:
        precision = pm4py.precision_alignments(log, net, initial_marking, final_marking)

    simplicity = simplicity_evaluator.apply(net)

    results = QualityResult(Fitness=fitness, Precision= precision, Simplicity= simplicity,Generalization= generalization)

    json_path = "src/temp/quality.json"
    with open(json_path, "w") as outfile:
        json.dump(results.json(), outfile)

    return json_path
