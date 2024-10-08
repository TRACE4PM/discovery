from datetime import datetime

import chardet
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
import time
import logging
import concurrent.futures
import sys


async def read_csv(file, case_name, concept_name, timestamp, separator):
    # read the csv file as dataframe
    with open(file, 'rb') as f:
        result = chardet.detect(f.read())
        encoding = result['encoding']

        # Read the file with the detected encoding
    dataframe = pd.read_csv(file, sep=';', encoding=encoding)
    # renaming the columns based on pm4py requirements
    dataframe.rename(columns={concept_name: 'concept:name'}, inplace=True)
    dataframe.rename(columns={case_name:'case:concept:name'}, inplace=True)
    dataframe.rename(columns={timestamp: 'time:timestamp'}, inplace=True)
    # Convert timestamp column to datetime and handle mixed format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format='mixed')

    return dataframe


async def read_files(file_path, case_name, concept_name, timestamp, separator):
    # read the log files depending on its extension
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        dataframe = await read_csv(file_path, case_name, concept_name, timestamp, separator)
        return dataframe
    elif extension == '.xes':
        log = pm4py.read_xes(file_path)
        return log
    else:
        raise ValueError('Wrong file format')


def latest_image():
    # get the path of the latest image stored in temp files

    tmp_dir = os.path.expanduser('/temp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image


def generate_zip(diagram_path, pnml_path, qual_path):

    timestamp_str = datetime.now().strftime("%m%d%H%M")  # add datetime to the models names

    # create a zip file containing the png of the model, its quality and the pnml file
    zip_path = f"temp/Zipped_file_{timestamp_str}.zip"
    with ZipFile(zip_path, 'w') as zip_object:
        # Adding files that need to be zipped
        zip_object.write(pnml_path, arcname=f'pnml_file_{timestamp_str}.pnml')

        name_png = os.path.split(diagram_path)

        zip_object.write(diagram_path, arcname=name_png[1])
        zip_object.write(qual_path, arcname=f"algo_quality_{timestamp_str}.json")

    # Remove the files from temp folder
    os.remove(diagram_path)
    os.remove(pnml_path)
    os.remove(qual_path)

    # Check to see if the zip file is created
    if os.path.exists(zip_path):
        return zip_path
    else:
        return "ZIP file not created"


def calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach):
    """
        Calculates the quality of the generated model
    Args:
        net,initial_marking, final_marking: petri net parameters
        fitness_approach, precision_approach: choosing the approach for fitness and precision, token-based or alignement

    Returns:

    """
    start_time = time.time()

    generalization_start = time.time()
    generalization = generalization_evaluator.apply(log, net, initial_marking, final_marking)

    fitness_start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if fitness_approach == "token based":
            future_fitness = executor.submit(pm4py.fitness_token_based_replay, log, net, initial_marking, final_marking)
        else:
            future_fitness = executor.submit(pm4py.fitness_alignments, log, net, initial_marking, final_marking)
        fitness = future_fitness.result()

    simplicity_start = time.time()
    simplicity = simplicity_evaluator.apply(net)

    precision_start = time.time()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        if precision_approach == "token based":
            future_precision = executor.submit(pm4py.precision_token_based_replay, log, net, initial_marking,
                                               final_marking)
        else:
            future_precision = executor.submit(pm4py.precision_alignments, log, net, initial_marking, final_marking)
        precision = future_precision.result()

    results = QualityResult(Fitness=fitness, Precision= precision, Simplicity=simplicity, Generalization=generalization)

    json_path = "temp/quality.json"
    json_write_start = time.time()
    with open(json_path, "w") as outfile:
        json.dump(results.json(), outfile)

    return results, json_path
