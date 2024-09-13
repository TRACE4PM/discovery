import logging
import os
from datetime import datetime
from http.client import HTTPException
import pm4py
import subprocess
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.alpha import variants
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.align_table import visualizer as diagram_visual
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.objects.conversion.dfg.variants import to_petri_net_invisibles_no_duplicates
from .utils import read_files, generate_zip, calculate_quality
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def alpha_miner_algo(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = alpha_miner.apply(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"alpha_petrinet_{timestamp_str}.png")

    diagram_visual.save(gviz, output_path)
    return log, net, initial_marking, final_marking, output_path, timestamp_str


async def alpha_algo_quality(file, case_name, concept_name, timestamp, separator, fitness_approach, precision_approach):
    log, net, initial_marking, final_marking, output_path, timestamp_str = await alpha_miner_algo(file, case_name, concept_name,
                                                                                   timestamp, separator)
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)

    pnml_path = os.path.join("temp", f"pnml_file_{timestamp_str}.pnml")
    pm4py.write.write_pnml(net, initial_marking, final_marking, pnml_path)

    zip_path = generate_zip(output_path, pnml_path, json_path)
    return results, zip_path


async def alpha_miner_plus(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = alpha_miner.apply(log, variant=variants.plus)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"alpha_plus_petrinet_{timestamp_str}.png")

    diagram_visual.save(gviz, output_path)
    return log, net, initial_marking, final_marking, output_path, timestamp_str


async def alpha_miner_plus_quality(file, case_name, concept_name, timestamp, separator, fitness_approach,
                                   precision_approach):
    log, net, initial_marking, final_marking, output_path, timestamp_str = await alpha_miner_plus(file, case_name, concept_name,
                                                                                   timestamp, separator)
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)

    pnml_path = os.path.join("temp", f"pnml_file_{timestamp_str}.pnml")
    pm4py.write.write_pnml(net, initial_marking, final_marking, pnml_path)

    zip_path = generate_zip(output_path, pnml_path, json_path)
    return results, zip_path


async def freq_alpha_miner(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = alpha_miner.apply(log)
    parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
    gviz = pn_visualizer.apply(net, initial_marking, final_marking, parameters=parameters,
                               variant=pn_visualizer.Variants.FREQUENCY, log=log)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"freq_miner_petrinet_{timestamp_str}.png")

    diagram_visual.save(gviz, output_path)
    return output_path


async def heuristic_miner(file, case_name, concept_name, timestamp, separator, dependency_threshold, and_threshold,
                          loop_two_threshold):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    heuristic_net = pm4py.discover_heuristics_net(log, activity_key='concept:name', case_id_key='case:concept:name',
                                                  timestamp_key='time:timestamp',
                                                  dependency_threshold=dependency_threshold,
                                                  and_threshold=and_threshold, loop_two_threshold=loop_two_threshold)
    gviz = hn_visualizer.apply(heuristic_net)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"heuristic_net_{timestamp_str}.png")

    hn_visualizer.save(gviz, output_path)
    return output_path


async def heuristic_miner_petri(file, case_name, concept_name, timestamp, separator, fitness_approach,
                                precision_approach):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = pm4py.discover_petri_net_heuristics(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"heuristic_petrinet_{timestamp_str}.png")

    diagram_visual.save(gviz, output_path)

    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)

    pnml_path = os.path.join("temp", f"pnml_file_{timestamp_str}.pnml")
    pm4py.write.write_pnml(net, initial_marking, final_marking, pnml_path)

    zip_path = generate_zip(output_path, pnml_path, json_path)
    return results, zip_path


async def inductive_miner(file, case_name, concept_name, timestamp, separator, noise_threshold):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"Inductive_Miner_{timestamp_str}.png")

    diagram_visual.save(gviz, output_path)
    return log, net, initial_marking, final_marking, output_path, timestamp_str


async def inductive_miner_quality(file, case_name, concept_name, timestamp, separator, noise_threshold,
                                  fitness_approach, precision_approach):
    log, net, initial_marking, final_marking, output_path, timestamp_str = await inductive_miner(file, case_name, concept_name,
                                                                                  timestamp, separator, noise_threshold)
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)

    pnml_path = os.path.join("temp", f"pnml_file_{timestamp_str}.pnml")
    pm4py.write.write_pnml(net, initial_marking, final_marking, pnml_path)

    zip_path = generate_zip(output_path, pnml_path, json_path)
    return results, zip_path


async def inductive_miner_tree(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    tree = pm4py.discover_process_tree_inductive(log)
    gviz = pt_visualizer.apply(tree)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"inductive_processTree_{timestamp_str}.png")

    pt_visualizer.save(gviz, output_path)
    return output_path


async def bpmn_model(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    bpmn_graph = pm4py.discover_bpmn_inductive(log)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"bpmn_model_{timestamp_str}.png")

    pm4py.save_vis_bpmn(bpmn_graph, output_path)
    return output_path


async def dfg_function(log):
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"DFG_{timestamp_str}.png")

    pm4py.save_vis_dfg(dfg, start_activities, end_activities, output_path)
    return dfg, start_activities, end_activities, output_path, timestamp_str


async def dfg_precision(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    dfg, start_activities, end_activities, output_path, timestamp_str = await dfg_function(log)
    precision = pm4py.algo.evaluation.precision.dfg.algorithm.apply(log, dfg, start_activities, end_activities)
    return precision, output_path


async def dfg_petri_quality(file, case_name, concept_name, timestamp, separator, fitness_approach="token based",
                            precision_approach="token based"):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    dfg, start_activities, end_activities, output_path, timestamp_str = await dfg_function(log)

    parameters = {to_petri_net_invisibles_no_duplicates.Parameters.START_ACTIVITIES: start_activities,
                  to_petri_net_invisibles_no_duplicates.Parameters.END_ACTIVITIES: end_activities}
    net, initial_marking, final_marking = to_petri_net_invisibles_no_duplicates.apply(dfg, parameters=parameters)
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)

    pnml_path = os.path.join("temp", f"pnml_file_{timestamp_str}.pnml")
    pm4py.write.write_pnml(net, initial_marking, final_marking, pnml_path)

    zip_path = generate_zip(output_path, pnml_path, json_path)
    return results, zip_path


async def dfg_performance(file, case_name, concept_name, timestamp, separator):
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)

    timestamp_str = datetime.now().strftime("%Y%m%d%H%M%S")
    output_dir = "temp"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"directly_follow_perfo_{timestamp_str}.png")

    pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, output_path)
    return output_path


async def process_animate(file_path):
    r_script_path = os.path.join(os.path.dirname(__file__), "file.R")
    res = subprocess.call(["Rscript", r_script_path, file_path])
    if res != 0:
        raise HTTPException(status_code=500, detail="R script execution failed")

    html_file_path = "temp/process_animation.html"

    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="HTML file not found")

    return html_file_path
