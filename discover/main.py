import logging
import os
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
    """
      Applying Alpha Miner algorithm on a log file and saving the model in a png file
    Args:
        separator:
        timestamp:
        concept_name:
        case_name:
        file: csv or xes log file
    Returns:
        petri net, initial marking and final marking
       """

    log = await read_files(file, case_name, concept_name, timestamp, separator)
    # applying alpha miner of the log file
    net, initial_marking, final_marking = alpha_miner.apply(log)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    output_path = "temp/alpha_petrinet.png"
    # save the petri net in a png file
    diagram_visual.save(gviz, output_path)
    return log, net, initial_marking, final_marking, output_path


async def alpha_algo_quality(file, case_name, concept_name, timestamp, separator, fitness_approach, precision_approach):
    """
    Args:
        file: csv or xes log file
        fitness_approach/ precision_approach: chose if token based or alignement based approach

    Returns:
        zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file
    """
    # applying alpha miner algorithm
    log, net, initial_marking, final_marking, output_path = await alpha_miner_algo(file, case_name, concept_name, timestamp, separator)

    # Calculate the quality of the resulting petri net of alpha miner
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)

    # Writing the pnml file of the petri net
    pm4py.write.write_pnml(net, initial_marking, final_marking, "temp/pnml_file.pnml")

    # Creating a zip file and saving the png, pnml and quality of the resulting model
    zip_path = generate_zip(output_path, "temp/pnml_file.pnml", json_path)
    return results, zip_path


async def alpha_miner_plus(file, case_name, concept_name, timestamp, separator):
    """
      Alpha miner plus :  able to discover more complex connections, handle loops and connections effectively

    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = alpha_miner.apply(log, variant=variants.plus)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)

    # save the petri net in a png file
    output_path = "temp/alpha_plus_petrinet.png"
    diagram_visual.save(gviz, output_path)
    return log, net, initial_marking, final_marking, output_path


async def alpha_miner_plus_quality(file, case_name, concept_name, timestamp, separator, fitness_approach, precision_approach):
    """
    Calculates the quality of the Alpha miner plus model
       Args:
           file: csv or xes log file
           fitness_approach/ precision_approach: chose if token based or alignement based approach

       Returns:
           zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file
       """
    log, net, initial_marking, final_marking, output_path = await alpha_miner_plus(file, case_name, concept_name, timestamp, separator)
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "temp/pnml_file.pnml")

    zip_path = generate_zip(output_path, "temp/pnml_file.pnml", json_path)

    return results, zip_path


async def freq_alpha_miner(file, case_name, concept_name, timestamp, separator):
    """
        Creates an Alpha miner petri net with the frequency of the activities and saves it in a png file
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)

    net, initial_marking, final_marking = alpha_miner.apply(log)
    parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
    gviz = pn_visualizer.apply(net, initial_marking, final_marking,
                               parameters=parameters,
                               variant=pn_visualizer.Variants.FREQUENCY,
                               log=log)
    # save the petri net in a png file
    output_path = "temp/freq_miner_petrinet.png"
    diagram_visual.save(gviz, output_path)
    return output_path


async def heuristic_miner(file, case_name, concept_name, timestamp, separator, dependency_threshold, and_threshold, loop_two_threshold):
    """
    Args:
        file: csv or xes log file
        parameter: can be null, so the heuristic net will be created with the default values of the
                parameters, or we chose a parameter (Dependency Threshold, And Threshold, or Loop Two Threshold)
        value: a float value of the parameter,

    Returns: a png file of the heuristic net
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    heuristic_net = pm4py.discover_heuristics_net(log, activity_key='concept:name',
                                                  case_id_key='case:concept:name', timestamp_key='time:timestamp',
                                                  dependency_threshold=dependency_threshold,
                                                  and_threshold=and_threshold,
                                                  loop_two_threshold=loop_two_threshold)
    gviz = hn_visualizer.apply(heuristic_net)
    output_path = "temp/heuristic_net.png"
    hn_visualizer.save(gviz, output_path)
    return output_path


async def heuristic_miner_petri(file, case_name, concept_name, timestamp, separator,
                                fitness_approach,
                                precision_approach):
    """
        Generate a petri net from a heuristic net to calculate the quality of the model
        Returns:
            A zip file containing the petri net, pnml file and the quality of the model
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)

    net, initial_marking, final_marking = pm4py.discover_petri_net_heuristics(log)

    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    output_path = "temp/heuristic_petrinet.png"
    diagram_visual.save(gviz, output_path)

    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "temp/pnml_file.pnml")

    zip_path = generate_zip(output_path, "temp/pnml_file.pnml", json_path)
    return results, zip_path


async def inductive_miner(file, case_name, concept_name, timestamp, separator, noise_threshold):
    """
        noise_threshold: a float value, filters noisy behavior, activities that are infrequent and outliers
            default value is 0
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)
    gviz = pn_visualizer.apply(net, initial_marking, final_marking)
    output_path = "temp/inductive_petrinet.png"
    diagram_visual.save(gviz, output_path)
    return log, net, initial_marking, final_marking, output_path


async def inductive_miner_quality(file, case_name, concept_name, timestamp, separator, noise_threshold, fitness_approach, precision_approach):
    """
    Args:
        file: csv/xes log file
        noise_threshold: a float value, filters noisy behavior, activities that are infrequent and outliers,
            default value is 0
        fitness_approach, precision_approach: chosing if token based or alignement based approach

    Returns:
        zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file

    """
    log, net, initial_marking, final_marking, output_path = await inductive_miner(file, case_name, concept_name, timestamp, separator, noise_threshold)

    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "temp/pnml_file")

    zip_path = generate_zip(output_path, "temp/pnml_file.pnml", json_path)

    return results, zip_path


async def inductive_miner_tree(file, case_name, concept_name, timestamp, separator):
    """
        Creates and inductive process tree and saves it in a png file
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    tree = pm4py.discover_process_tree_inductive(log)
    gviz = pt_visualizer.apply(tree)
    output_path = "temp/inductive_processTree.png"
    pt_visualizer.save(gviz, output_path)
    return output_path


async def bpmn_model(file, case_name, concept_name, timestamp, separator):
    """
       Creates and inductive BPMN model and saves it in a png file
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator )
    bpmn_graph = pm4py.discover_bpmn_inductive(log)
    output_path = "temp/bpmn_model.png"
    pm4py.save_vis_bpmn(bpmn_graph, output_path)
    return output_path


async def dfg_function(log):
    """
        Generates a graph of the directly follow activities and saves it in a png file
    Returns:
        A tuple with the directly-following activities
    """
    dfg, start_activities, end_activities = pm4py.discover_dfg(log)
    output_path = "temp/directly_follow.png"
    pm4py.save_vis_dfg(dfg, start_activities, end_activities, output_path)

    return dfg, start_activities, end_activities, output_path


async def dfg_precision(file, case_name, concept_name, timestamp, separator):
    """
        Returns : the precision of the Directly Follow Graph
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    dfg, start_activities, end_activities, output_path = await dfg_function(log)
    precision = pm4py.algo.evaluation.precision.dfg.algorithm.apply(log, dfg, start_activities, end_activities)
    return precision, output_path


async def dfg_petri_quality(file, case_name, concept_name, timestamp, separator, fitness_approach: str = "token based",
                            precision_approach: str = "token based"):
    """
     Converts the dfg to a petri net to calculate the quality of the resulting model
    Returns:
        zip file: containing a json file of the quality of the model, a png of the petri net and a PNML file
    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)

    dfg, start_activities, end_activities, output_path = await dfg_function(log)
    parameters = {to_petri_net_invisibles_no_duplicates.Parameters.START_ACTIVITIES: start_activities,
                  to_petri_net_invisibles_no_duplicates.Parameters.END_ACTIVITIES: end_activities}

    net, initial_marking, final_marking = to_petri_net_invisibles_no_duplicates.apply(dfg, parameters=parameters)
    results, json_path = calculate_quality(log, net, initial_marking, final_marking, fitness_approach,
                                           precision_approach)
    pm4py.write.write_pnml(net, initial_marking, final_marking, "temp/pnml_file")

    zip_path = generate_zip("temp/directly_follow.png", "temp/pnml_file.pnml", json_path)
    return results, zip_path


async def dfg_performance(file, case_name, concept_name, timestamp, separator):
    """
        Discovers a performance directly-follows graph from an event log and saves it in a png file

    """
    log = await read_files(file, case_name, concept_name, timestamp, separator)
    performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)
    output_path = "temp/directly_follow_perfo.png"
    pm4py.save_vis_performance_dfg(performance_dfg, start_activities, end_activities,
                                   output_path)
    return output_path


async def process_animate(file_path):
    """
      Opens an html page showing an animation of the DFG model using processanimateR library

    """
    # Call the R function with the file path
    r_script_path = os.path.join(os.path.dirname(__file__), "file.R")
    res = subprocess.call(["Rscript", r_script_path, file_path])
    if res != 0:
        raise HTTPException(status_code=500, detail="R script execution failed")

    html_file_path = "temp/process_animation.html"

    if not os.path.exists(html_file_path):
        raise HTTPException(status_code=404, detail="HTML file not found")

    # Read and return the HTML content

    return html_file_path