import os
import io
import glob
import pandas as pd
import tempfile
import pm4py
import json
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from zipfile import ZipFile
# from pm4py.algo.simulation.playout.petri_net import algorithm as simulator
# from pm4py.statistics.variants.log import get as variants_module
# from pm4py.algo.evaluation.earth_mover_distance import algorithm as emd_evaluator



async def read_csv(file):
    # file_content = await file.read()
    dataframe = pd.read_csv(file, sep=";")

    # renaming the col ending with _id
    dataframe.rename(columns=lambda x: 'case:concept:name' if x.endswith('_id') else x, inplace=True)
    dataframe.rename(columns=lambda x: 'time:timestamp' if x.endswith('timestamp') else x, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)

    # Convert timestamp column to datetime and handle mixed format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format='mixed')

    dataframe = pm4py.format_dataframe(dataframe, case_id='case:concept:name', activity_key='concept:name',
                                       timestamp_key='time:timestamp')
    log = pm4py.convert_to_event_log(dataframe)

    return log


# async def read_files(file):
#     file_content = await file.read()
#     with tempfile.NamedTemporaryFile(delete=False) as temp_file:
#         temp_file.write(file_content)
#         temp_file_path = temp_file.name
#         if file.filename.endswith('.csv'):
#             log = await read_csv(file_content)
#         elif file.filename.endswith('.xes'):
#             log = pm4py.read_xes(temp_file_path)
#
#     os.remove(temp_file_path)
#     return log

async def read_files(file_path):
    extension = os.path.splitext(file_path)[1].lower()
    if extension == '.csv':
        log = await read_csv(file_path)
    elif extension == '.xes':
        log = pm4py.read_xes(file_path)
    return log


def latest_image():
    tmp_dir = os.path.expanduser('/tmp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image


def generate_zip(diagram_path, pnml_path, qual_path):
    zip_path = "src/temp/Zipped_file.zip"
    with ZipFile(zip_path, 'w') as zip_object:
        # Adding files that need to be zipped
        zip_object.write(pnml_path,arcname='pnml_file.pnml')

        name_png = os.path.split(diagram_path)
        zip_object.write(diagram_path, arcname = name_png[1])
        zip_object.write(qual_path, arcname="algo_quality.json")

    # Check to see if the zip file is created
    if os.path.exists(zip_path):
        return "ZIP file created :", zip_path
    else:
        return "ZIP file not created"


def calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach):
    gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
    if fitness_approach == "token based":
        fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking)
    else:
        fitness = pm4py.fitness_alignments(log, net, initial_marking, final_marking)
    if precision_approach == "token based":
        prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking)
    else:
        prec = pm4py.precision_alignments(log, net, initial_marking, final_marking)

    simp = simplicity_evaluator.apply(net)

    # edm = earth_distance(log, net, initial_marking, final_marking)

    results = {"Fitness": fitness,
               "Precision": prec,
               "Generalization": gen,
               "Simplicity": simp,
              }

    json_path = "src/temp/quality.json"
    with open(json_path, "w") as outfile:
        json.dump(results, outfile)

    return json_path

#
# def earth_distance(log, net, im, fm):
#
#     # language mean a set of traces that is weighted according to its probability.
#     language = variants_module.get_language(log)
#
#     net, im, fm = alpha_miner.apply(log)
#     playout_log = simulator.apply(net, im, fm,
#                                   parameters={simulator.Variants.STOCHASTIC_PLAYOUT.value.Parameters.LOG: log},
#                                   variant=simulator.Variants.STOCHASTIC_PLAYOUT)
#     model_language = variants_module.get_language(playout_log)
#
#     emd = emd_evaluator.apply(model_language, language)
#     return emd