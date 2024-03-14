import os
import io
import glob
import pandas as pd
import tempfile
import pm4py
from zipfile import ZipFile

async def read_csv(file_content):
    dataframe = pd.read_csv(io.StringIO(file_content.decode('utf-8')), sep=';')

    dataframe.rename(columns={'@timestamp': 'time:timestamp'}, inplace=True)
    dataframe.rename(columns={'action': 'concept:name'}, inplace=True)
    dataframe.rename(columns={'session_id': 'case:concept:name'}, inplace=True)

    # Specify the timestamp format
    timestamp_format = "%Y-%m-%d %H:%M:%S.%f"

    # Convert timestamp column to datetime format with specified format
    dataframe['time:timestamp'] = pd.to_datetime(dataframe['time:timestamp'], format=timestamp_format)

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

def generate_zip(diagram_path, pnml_path, qual_path):
    zip_path = "/home/ania/Desktop/trace_clustering/services/discover/outputs/Zipped_file.zip"
    with ZipFile(zip_path, 'w') as zip_object:
        # Adding files that need to be zipped
        zip_object.write(pnml_path,
                         arcname='pnml_file')
        zip_object.write(diagram_path, arcname="gviz_diagram")
        zip_object.write(qual_path, arcname="algo_quality")


    # Check to see if the zip file is created
    if os.path.exists(zip_path):
        print("ZIP file created")
    else:
        print("ZIP file not created")

