import asyncio
from discover.main import ( alpha_miner_plus_quality,heuristic_miner, dfg_precision, process_animate,
                            heuristic_miner_petri)

file_path = '/home/ania/Desktop/trace_clustering/services/clustering/test/result_res10k.csv'

async def main():

    #### **************** testing the functions **********

    print(await alpha_miner_plus_quality(file_path, "token based", "token based"))
    # await heuristic_miner(file_path, 0.5 , 0.5,0.9 )

    # await process_animate(file_path)
    # print(await dfg_precision(file_path))
    # await heuristic_miner_petri(file_path, "token based", "token based")


if __name__ == "__main__":
    asyncio.run(main())
