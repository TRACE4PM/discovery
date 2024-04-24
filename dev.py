import subprocess
import asyncio
import pm4py
from discover.main import (alpha_miner_algo, alpha_algo_quality)
import os
from discover.utils import read_files
#
#
async def alph():
    file_path = '/home/ania/Desktop/trace_clustering/services/clustering/test/result_res10k.csv'
    await alpha_algo_quality(file_path,'token based', 'token based')


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