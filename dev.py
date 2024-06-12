import asyncio
from discover.main import ( alpha_miner_algo, alpha_algo_quality,alpha_miner_plus_quality,heuristic_miner, dfg_precision, process_animate,
                            heuristic_miner_petri, inductive_miner)

file_path = '/home/ania/Desktop/trace_clustering/services/clustering/temp/logs/cluster_log_0.csv'
# file_path = '/home/ania/Desktop/test/fss/fss-99-2/files/Cluster0_Logs.csv'

async def main():

    #### **************** testing the functions **********

    # print(await inductive_miner(file_path,'client_id', 'action', 'timestamp', ";", 0.5))
    # await heuristic_miner(file_path, 'client_id', 'action', 'timestamp', ";",0.5 , 0.65,0.5 )
    await alpha_miner_algo(file_path, 'client_id', 'action', 'timestamp', ";")

    # print(await dfg_precision(file_path, 'client_id', 'action', 'timestamp', ";"))
    print(await heuristic_miner_petri(file_path, 'client_id', 'action', 'timestamp', ";","token based", "token based"))

    # await process_animate(file_path)

if __name__ == "__main__":
    asyncio.run(main())
