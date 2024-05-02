import os
import pm4py
import subprocess
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.algo.discovery.alpha import variants
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.visualization.align_table import visualizer as diagram_visual
from pm4py.visualization.heuristics_net import visualizer as hn_visualizer
from pm4py.visualization.process_tree import visualizer as pt_visualizer
from pm4py.objects.conversion.dfg.variants import to_petri_net_invisibles_no_duplicates
from .utils import read_files, latest_image, generate_zip, calculate_quality
from .models.qual_params import HeuristicParameters


async def alpha_function(log):
   """
    applying alpha miner algorithm on a log file
    Returns: petri net, initial marking and final marking
   """
   net, initial_marking, final_marking = alpha_miner.apply(log)
   gviz = pn_visualizer.apply(net, initial_marking, final_marking)

   # save the petri net in a png file
   diagram_visual.save(gviz, "src/temp/alpha_petrinet.png")
   return net, initial_marking, final_marking


async def alpha_miner_algo(file):
    log = await read_files(file)
    await alpha_function(log)


async def alpha_algo_quality(file, fitness_approach, precision_approach):
    """

    Args:
        file:
        fitness_approach/ precision_approach: chose if token based or alignement based approach

    Returns:
        zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file

    """
    log = await read_files(file)
    net, initial_marking, final_marking = await alpha_function(log)

    json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "src/temp/pnml_file.pnml")

    zip_path = generate_zip("src/temp/alpha_petrinet.png", "src/temp/pnml_file.pnml", json_path)
    return zip_path


# alpha miner plus able to discover more complex connections, handle loops and connections effectively7
async def miner_plus_function(log):
    net, initial_marking, final_marking = alpha_miner.apply(log, variant=variants.plus)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    diagram_visual.save(gviz, "src/temp/alpha_plus_petrinet.png")
    return net, initial_marking, final_marking


async def alpha_miner_plus(file):
    log = await read_files(file)
    await miner_plus_function(log)


async def alpha_miner_plus_quality(file, fitness_approach: str = "token based",
                                   precision_approach: str = "token based"):
    log = await read_files(file)
    net, initial_marking, final_marking = await miner_plus_function(log)

    json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "src/temp/pnml_file.pnml")

    zip_path = generate_zip("src/temp/alpha_plus_petrinet.png", "src/temp/pnml_file.pnml", json_path)

    return zip_path


async def freq_alpha_miner(file):
    log = await read_files(file)

    net, initial_marking, final_marking = alpha_miner.apply(log)
    parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
    gviz = pn_visualizer.apply(net, initial_marking, final_marking,
                               parameters=parameters,
                               variant=pn_visualizer.Variants.FREQUENCY,
                               log=log)
    output_path = "src/temp/freq_miner_petrinet.png"
    diagram_visual.save(gviz, output_path)


async def heuristic_miner(file):
    log = await read_files(file)
    heuristic_net = pm4py.discover_heuristics_net(log, activity_key='concept:name', case_id_key='case:concept:name',
                                                  timestamp_key='time:timestamp')
    gviz = hn_visualizer.apply(heuristic_net)
    hn_visualizer.save(gviz, "src/temp/heuristic_net.png")


async def heuristic_miner_petri(file, fitness_approach: str = "token based",
                                precision_approach: str = "token based"):
    log = await read_files(file)
    net, initial_marking, final_marking = pm4py.discover_petri_net_heuristics(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    diagram_visual.save(gviz, "src/temp/heuristic_petrinet.png")

    json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "src/temp/pnml_file.pnml")

    zip_path = generate_zip("src/temp/heuristic_petrinet.png", "src/temp/pnml_file.pnml", json_path)

    return zip_path


async def heuristic_params_threshold(file, parameter: HeuristicParameters, value: float):
    log = await read_files(file)

    if parameter.lower() == "dependency threshold":
        heuristic_net = pm4py.discover_heuristics_net(log, activity_key='concept:name',
                                                      case_id_key='case:concept:name',
                                                      timestamp_key='time:timestamp', dependency_threshold=value)
    elif parameter.lower() == "and threshold":
        heuristic_net = pm4py.discover_heuristics_net(log, activity_key='concept:name',
                                                      case_id_key='case:concept:name',
                                                      timestamp_key='time:timestamp', and_threshold=value)
    elif parameter.lower() == "loop two threshold":
        heuristic_net = pm4py.discover_heuristics_net(log, activity_key='concept:name',
                                                      case_id_key='case:concept:name',
                                                      timestamp_key='time:timestamp', loop_two_threshold=value)
    else:
        raise ValueError("Invalid parameter name")

    gviz = hn_visualizer.apply(heuristic_net)
    hn_visualizer.save(gviz, "src/temp/heuristic_net.png")


async def inductive_miner_function(log, noise_threshold):
    # noise threshold: filters noisy behavior, activities that are infrequent and outliers
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    diagram_visual.save(gviz, "src/temp/inductive_petrinet.png")
    return net, initial_marking, final_marking


async def inductive_miner(file, noise_threshold):
    log = await read_files(file)
    # noise threshold: filters noisy behavior, activities that are infrequent and outliers
    await inductive_miner_function(log, noise_threshold)


async def inductive_miner_quality(file, noise_threshold, fitness_approach: str = "token based",
                                  precision_approach: str = "token based"):
    log = await read_files(file)

    # noise threshold: filters noisy behavior, activities that are infrequent and outliers
    net, initial_marking, final_marking = await inductive_miner_function(log, noise_threshold)

    json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "src/temp/pnml_file")

    zip_path = generate_zip("src/temp/inductive_petrinet.png", "src/temp/pnml_file.pnml", json_path)

    return zip_path


async def inductive_miner_tree(file):
    log = await read_files(file)
    tree = pm4py.discover_process_tree_inductive(log)
    pm4py.view_process_tree(tree)
    gviz = pt_visualizer.apply(tree)
    pt_visualizer.save(gviz, "src/temp/inductive_processTree.png")


async def dfg_function(log):
    dfg, start_activities, end_activities = pm4py.discover_dfg(log, case_id_key='case:concept:name',
                                                               activity_key='concept:name',
                                                               timestamp_key='time:timestamp')
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, "src/temp/directly_follow.png")

    return dfg, start_activities, end_activities


async def directly_follow(file):
    log = await read_files(file)
    dfg, start_activities, end_activities = await dfg_function(log)
    precision = pm4py.algo.evaluation.precision.dfg.algorithm.apply(log, dfg, start_activities, end_activities)
    return precision


async def dfg_petri_quality(file, fitness_approach: str = "token based", precision_approach: str = "token based"):
    log = await read_files(file)

    dfg, start_activities, end_activities = await dfg_function(log)
    parameters = {to_petri_net_invisibles_no_duplicates.Parameters.START_ACTIVITIES: start_activities,
                  to_petri_net_invisibles_no_duplicates.Parameters.END_ACTIVITIES: end_activities}

    net, initial_marking, final_marking = to_petri_net_invisibles_no_duplicates.apply(dfg, parameters=parameters)
    json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach, precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "src/temp/pnml_file")

    zip_path = generate_zip("src/temp/directly_follow.png", "src/temp/pnml_file.pnml", json_path)
    return zip_path


async def dfg_performance(file):
    log = await read_files(file)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)
    pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities, "src/temp/directly_follow_perfo.png")


async def bpmn_model(file):
    log = await read_files(file)
    bpmn_graph = pm4py.discover_bpmn_inductive(log)
    pm4py.save_vis_bpmn(bpmn_graph, "src/temp/bpmn_model.png")


async def process_animate(file_path):
    # Call the R function with the file path
    r_script_path = os.path.join(os.path.dirname(__file__), "file.R")
    res = subprocess.call(["Rscript", r_script_path, file_path])
    return res
