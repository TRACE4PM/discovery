import os
import io
import glob
import pm4py
import pandas as pd
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query, Request, Depends
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.align_table import visualizer as diagram_visual
from pm4py.algo.discovery.alpha import variants
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.objects.conversion.dfg.variants import to_petri_net_invisibles_no_duplicates
import tempfile
import subprocess
from .models.qual_params import MiningResult
from .utils import read_files, latest_image, generate_zip, calculate_quality
import json


async def alpha_miner_alg(file, sep):
    log = await read_files(file, sep)
    net, initial_marking, final_marking = alpha_miner.apply(log)

    return log, net, initial_marking, final_marking


# able to discover more complex connection, handle loops and connections effectively
async def alpha_miner_plus(file,sep):
    log = await read_files(file, sep)
    net, initial_marking, final_marking = alpha_miner.apply(log, variant=variants.plus)
    return log, net, initial_marking, final_marking


async def freq_alpha_miner(file, sep):
    log = await read_files(file, sep)

    net, initial_marking, final_marking = alpha_miner.apply(log)
    parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
    gviz = pn_visualizer.apply(net, initial_marking, final_marking,
                               parameters=parameters,
                               variant=pn_visualizer.Variants.FREQUENCY,
                               log=log)
    return gviz


async def heuristic_miner(file, sep):
    log = await read_files(file, sep)
    heu_net = pm4py.discover_heuristics_net(log, activity_key='concept:name', case_id_key='case:concept:name',
                                            timestamp_key='time:timestamp')
    # pm4py.view_heuristics_net(heu_net)
    return heu_net


async def heuristic_miner_petri(file, sep):
    log = await read_files(file, sep)
    net, im, fm = pm4py.discover_petri_net_heuristics(log)
    # pm4py.view_petri_net(net, im, fm)
    return net, im, fm


async def heuristic_params_threshold(file, sep,
                                     value):
    log = await read_files(file, sep)

    heu_net = pm4py.discover_heuristics_net(log, activity_key='concept:name', case_id_key='case:concept:name',
                                            timestamp_key='time:timestamp', dependency_threshold=value)

    # parameters to test
    # 1) dependency_threshold : def 0.5   (filter out weaker dependencies )
    # 2) and_threshold    def: 0.65   (activities that occur in the same time )
    # 3) loop_two_threshold    def : 0.5   (minimum frequency required for a loop to be considered significant )

    # pm4py.view_heuristics_net(heu_net)
    return heu_net


async def inductive_miner(file, sep, noise_threshold):
    log = await read_files(file, sep)
    # noise threshold: filters noisy behavior, activities that are infrequent and outliers
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)

    return log, net, initial_marking, final_marking


#
# async def inductive_miner_quality(file, noise_threshold):
#         log = await read_files(file)
#
#         # noise threshold: filters noisy behavior, activities that are infrequent and outliers
#         net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)
#
#         pm4py.save_vis_petri_net(net, initial_marking, final_marking, 'outputs/diagram.png')
#
#         # pn_visualizer.apply(net, initial_marking, final_marking).view()
#
#         json_path = calculate_quality(log, net, initial_marking, final_marking)
#         pm4py.write.write_pnml(net, im, fm, "src/outputs/pnml_file")
#
#         zip = generate_zip("src/outputs/diagram.png", "src/outputs/pnml_file.pnml", json_path)
#
#         return zip
#

async def inductive_miner_tree(file, sep):
    log = await read_files(file, sep)
    tree = pm4py.discover_process_tree_inductive(log)
    # pm4py.view_process_tree(tree)
    return tree


async def directly_follow(file, sep):
    log = await read_files(file, sep)

    dfg, start_activities, end_activities = pm4py.discover_dfg(log, case_id_key='case:concept:name',
                                                               activity_key='concept:name',
                                                               timestamp_key='time:timestamp')
    # pm4py.view_dfg(dfg, start_activities, end_activities)
    # precision = pm4py.algo.evaluation.precision.dfg.algorithm.apply(log, dfg, start_activities, end_activities)

    # results = {"precision": str(precision)}
    return dfg, start_activities, end_activities


async def dfg_to_petrinet(file, sep):
    log = await read_files(file, sep)

    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    # pm4py.view_dfg(dfg, start_activities, end_activities)
    # pm4py.save_vis_dfg(dfg, start_activities, end_activities, 'outputs/dfg.png')
    parameters = {to_petri_net_invisibles_no_duplicates.Parameters.START_ACTIVITIES: start_activities,
                  to_petri_net_invisibles_no_duplicates.Parameters.END_ACTIVITIES: end_activities}

    net, initial_marking, final_marking = to_petri_net_invisibles_no_duplicates.apply(dfg, parameters=parameters)
    # gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    return log, net, initial_marking, final_marking


async def dfg_perfor(file, sep):
    log = await read_files(file, sep)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)
    # pm4py.view_performance_dfg(performance_dfg, start_activities, end_activities)
    return performance_dfg, start_activities, end_activities


async def bpmn_model(file, sep):
    log = await read_files(file, sep)
    process_tree = pm4py.discover_process_tree_inductive(log)
    # Convert the process tree to a BPMN model
    bpmn_model = pm4py.convert_to_bpmn(process_tree)
    # pm4py.view_bpmn(bpmn_model)
    #
    # bpmn_file_path = 'test.bpmn'
    #
    # with tempfile.NamedTemporaryFile(delete=False, suffix='.bpmn') as temp_file:
    #     pm4py.write_bpmn(bpmn_model, temp_file.name)
    #     bpmn_file_path = temp_file.name
    #
    # print("BPMN model exported to:", bpmn_file_path)
    return bpmn_model


async def process_animate(file_path):
    # Save the uploaded file
    # file_path = os.path.join("src/logs", file.filename)
    # with open(file_path, "wb") as f:
    #     contents = await file.read()
    #     f.write(contents)

    # Call the R function with the file path
    r_script_path = os.path.join(os.path.dirname(__file__), "file.R")
    res = subprocess.call(["Rscript", r_script_path, file_path])
    return res
