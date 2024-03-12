import os
import glob
import pandas as pd

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

