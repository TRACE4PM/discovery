import subprocess
import asyncio
import pm4py
from discover.main import (alpha_miner_alg, alpha_miner_quality, heuristic_miner, inductive_miner,
                           heuristic_params_threshold, inductive_miner_tree,inductive_miner_quality, dfg_to_petrinet)
from discover.utils import read_files
#
#
async def alph():
    # file = '/home/ania/Desktop/trace_clustering/services/discover/test/running-example.xes'
    file = '/home/ania/Desktop/trace_clustering/services/discover/test/Digital-Library-logs.csv'
    result = await alpha_miner_alg(file)
    print(result)

async def main():
    await alph()


#
if __name__ == "__main__":
    asyncio.run(main())


#
# res = subprocess.call("Rscript discover/file.R", shell=True)
#
# res
#