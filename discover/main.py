import os
import glob
import pm4py
import pandas as pd
from fastapi import FastAPI, UploadFile, File, APIRouter, HTTPException, Query,Request,  Depends
from pm4py.algo.discovery.alpha import algorithm as alpha_miner
from pm4py.visualization.petri_net import visualizer as pn_visualizer
from pm4py.algo.discovery.alpha import variants
from pm4py.algo.evaluation.generalization import algorithm as generalization_evaluator
from pm4py.algo.evaluation.simplicity import algorithm as simplicity_evaluator
from pm4py.objects.conversion.dfg.variants import to_petri_net_invisibles_no_duplicates
import tempfile
import subprocess
from .models.qual_params import MiningResult

async def alpha_miner_alg(file: UploadFile = File(...)):
        log = await read_files(file)
        net, initial_marking, final_marking = alpha_miner.apply(log)
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.view(gviz)


async def alpha_miner_quality(file: UploadFile = File(...)):
        log = await read_files(file)
        net, initial_marking, final_marking = alpha_miner.apply(log)
        # Model evaluation :

        gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
        fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking)
        prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking)
        simp = simplicity_evaluator.apply(net)

        results = {"Fitness": fitness,
                   "Precision": prec,
                   "Generalization": gen,
                   "Simplicity": simp}

        return MiningResult(**results)


# able to discover more complex connection, handle loops and connections effectively

async def alpha_miner_plus(file: UploadFile = File(...)):
        log = await read_files(file)
        net, initial_marking, final_marking = alpha_miner.apply(log, variant=variants.plus)
        gviz = pn_visualizer.apply(net, initial_marking, final_marking)
        pn_visualizer.view(gviz)



async def alpha_plus_quality(file: UploadFile = File(...)):
        log = await read_files(file)
        net, initial_marking, final_marking = alpha_miner.apply(log, variant=variants.plus)
        # Model evaluation
        gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
        fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking)
        prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking)
        simp = simplicity_evaluator.apply(net)

        results = {"Fitness": fitness,
                   "Precision": prec,
                   "Generalization": gen,
                   "Simplicity": simp}

        return MiningResult(**results)




async def freq_alpha_miner(file: UploadFile = File(...)):
        log = await read_files(file)

        net, initial_marking, final_marking = alpha_miner.apply(log)
        parameters = {pn_visualizer.Variants.FREQUENCY.value.Parameters.FORMAT: "png"}
        gviz = pn_visualizer.apply(net, initial_marking, final_marking,
                                   parameters=parameters,
                                   variant=pn_visualizer.Variants.FREQUENCY,
                                   log=log)
        pn_visualizer.view(gviz)


async def heuristic_miner(file: UploadFile = File(...)):
        log = await read_files(file)
        heu_net = pm4py.discover_heuristics_net(log, activity_key='concept:name', case_id_key='case:concept:name',
                                                timestamp_key='time:timestamp')
        pm4py.view_heuristics_net(heu_net)


async def heuristic_miner(file: UploadFile = File(...)):
        log = await read_files(file)
        net, im, fm = pm4py.discover_petri_net_heuristics(log)
        pm4py.view_petri_net(net, im, fm)


async def heuristic_params_threshold(file: UploadFile = File(...),
                                     value: float = Query(0.5, ge=0, le=1)):
        log = await read_files(file)

        heu_net = pm4py.discover_heuristics_net(log, activity_key='concept:name', case_id_key='case:concept:name',
                                                timestamp_key='time:timestamp', dependency_threshold=value)

        # parameters to test
        # 1) dependency_threshold : def 0.5   (filter out weaker dependencies )
        # 2) and_threshold    def: 0.65   (activities that occur in the same time )
        # 3) loop_two_threshold    def : 0.5   (minimum frequency required for a loop to be considered significant )

        pm4py.view_heuristics_net(heu_net)


async def inductive_miner(file: UploadFile = File(...),
                          noise_threshold: float = Query(0, ge=0, le=1)):
        log = await read_files(file)

        # noise threshold: filters noisy behavior, activities that are infrequent and outliers
        net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)
        pn_visualizer.apply(net, initial_marking, final_marking).view()


async def inductive_miner(file: UploadFile = File(...),
                          noise_threshold: float = Query(0, ge=0, le=1)):
        log = await read_files(file)

        # noise threshold: filters noisy behavior, activities that are infrequent and outliers
        net, initial_marking, final_marking = pm4py.discover_petri_net_inductive(log, noise_threshold)
        # pn_visualizer.apply(net, initial_marking, final_marking).view()

        # Model evaluation
        gen = generalization_evaluator.apply(log, net, initial_marking, final_marking)
        fitness = pm4py.fitness_token_based_replay(log, net, initial_marking, final_marking)
        prec = pm4py.precision_token_based_replay(log, net, initial_marking, final_marking)
        simp = simplicity_evaluator.apply(net)

        results = {
            "Fitness": fitness,
            "Precision": prec,
            "Generalization": gen,
            "Simplicity": simp
        }
        return MiningResult(**results)



async def inductive_miner_tree(file: UploadFile = File(...)):
        log = await read_files(file)
        tree = pm4py.discover_process_tree_inductive(log)
        pm4py.view_process_tree(tree)


async def directly_follow(file: UploadFile = File(...)):
        log = await read_files(file)

        dfg, start_activities, end_activities = pm4py.discover_dfg(log)
        pm4py.view_dfg(dfg, start_activities, end_activities)
        precision = pm4py.algo.evaluation.precision.dfg.algorithm.apply(log, dfg, start_activities, end_activities)

        results = {"precision": str(precision)}
        return results



async def dfg_to_petrinet(file: UploadFile = File(...)):
        log = await read_files(file)

        dfg, start_activities, end_activities = pm4py.discover_dfg(log)
        pm4py.view_dfg(dfg, start_activities, end_activities)

        parameters = {to_petri_net_invisibles_no_duplicates.Parameters.START_ACTIVITIES: start_activities,
                      to_petri_net_invisibles_no_duplicates.Parameters.END_ACTIVITIES: end_activities}

        net, im, fm = to_petri_net_invisibles_no_duplicates.apply(dfg, parameters=parameters)
        pn_visualizer.apply(net, im, fm).view()

        # gen = generalization_evaluator.apply(log, net, im, fm)
        # fitness = pm4py.fitness_token_based_replay(log, net, im, fm)
        # prec = pm4py.precision_token_based_replay(log, net, im, fm)
        # simp = simplicity_evaluator.apply(net)
        #
        # result_data = {
        #     "Generalization": gen,
        #     "Fitness": fitness,
        #     "Precision": prec,
        #     "Simplicity": simp
        # }




async def dfg_perfo(file: UploadFile = File(...)):
        log = await read_files(file)
        performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(log)
        pm4py.view_performance_dfg(performance_dfg, start_activities, end_activities)


async def bpmn_mod(file: UploadFile = File(...)):
        file_content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_content)
            temp_file_path = temp_file.name
            if file.filename.endswith('.csv'):
                log = await read_csv(file_content)
            else:
                log = pm4py.read_xes(temp_file_path)

        process_tree = pm4py.discover_process_tree_inductive(log)
        # Convert the process tree to a BPMN model
        bpmn_model = pm4py.convert_to_bpmn(process_tree)
        pm4py.view_bpmn(bpmn_model)
        #
        # bpmn_file_path = 'test.bpmn'
        #
        # with tempfile.NamedTemporaryFile(delete=False, suffix='.bpmn') as temp_file:
        #     pm4py.write_bpmn(bpmn_model, temp_file.name)
        #     bpmn_file_path = temp_file.name
        #
        # print("BPMN model exported to:", bpmn_file_path)



async def process_animate(request: Request):
        # with open("temp.xes", "wb") as temp_file:
        #     temp_file.write(await file.read())

        r_script_path = os.path.join(os.path.dirname(__file__), "file.R")
        res = subprocess.call(["Rscript",r_script_path])

        if res != 0:
            raise HTTPException(status_code=500, detail="R script execution failed.")

        # tmp_dir = os.path.expanduser('/app')
        # list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
        # latest_image = max(list_of_files, key=os.path.getctime)
        # print(latest_image)

        # templates = Jinja2Templates(directory="templates")
        #
        # return templates.TemplateResponse(
        #      "animate_csv.html", context={}
        # )
        # return templates.TemplateResponse(request=request,"animate_csv.html",{"file_path": latest_image})


async def read_csv(file_content):
    dataframe = pd.read_csv(io.StringIO(file_content.decode('utf-8')), sep=';')

    dataframe.rename(columns={'@timestamp': 'time:timestamp'}, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)
    dataframe.rename(columns={'session_id': 'case:concept:name'}, inplace=True)
    # Convert timestamp column to datetime format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'])
    dataframe = pm4py.format_dataframe(dataframe, case_id='case:concept:name', activity_key='concept:name',
                                       timestamp_key='time:timestamp')
    log = pm4py.convert_to_event_log(dataframe)

    return log


async def read_files(file):
    file_content = await file.read()
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(file_content)
        temp_file_path = temp_file.name
        if file.filename.endswith('.csv'):
            log = await read_csv(file_content)
        else:
            log = pm4py.read_xes(temp_file_path)

    os.remove(temp_file_path)

    return log

def latest_image():
    tmp_dir = os.path.expanduser('/tmp')
    list_of_files = glob.glob(os.path.join(tmp_dir, '*'))
    latest_image = max(list_of_files, key=os.path.getctime)

    return latest_image


