import asyncio
from discover.main import ( alpha_miner_algo, alpha_algo_quality,alpha_miner_plus_quality,heuristic_miner, dfg_precision,
                            process_animate, inductive_miner_quality,
                            heuristic_miner_petri, inductive_miner, dfg_petri_quality, inductive_miner_tree)

# file_path = '/home/ania/Desktop/test/trace based/file/cluster_log_3.csv'
file_path = '/home/ania/Desktop/test/fss/fss-99-2/files/Cluster2_Logs.csv'

async def main():

    #### **************** testing the functions **********

    # await inductive_miner_tree(file_path, 'client_id', 'action', 'timestamp', ";")
    #
    # await inductive_miner(file_path,'client_id', 'action', 'timestamp', ";", 1)
    # await heuristic_miner(file_path, 'client_id', 'action', 'timestamp', ";",0.5 , 0.65,0.5 )
    # print(await dfg_precision(file_path,'client_id', 'action', 'timestamp', ";" ))

    # print(await inductive_miner_quality(file_path, 'client_id', 'action', 'timestamp', ";", 1, "token based","token based"))
    # print(await dfg_petri_quality(file_path, 'client_id', 'action', 'timestamp', ";","token based", "token based" ))
    # print(await dfg_petri_quality(file_path, 'client_id', 'action', 'timestamp', ";","token based", "token based"))

    await process_animate(file_path)

if __name__ == "__main__":
    asyncio.run(main())
