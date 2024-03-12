import subprocess
import asyncio
from discover.main import alpha_miner_alg, alpha_miner_quality
#
#
# async def alph():
#     file = '/home/ania/Desktop/trace_clustering/services/discover/test/Digital-Library-logs.csv'
#     await alpha_miner_quality(file)
#
#
#
# async def main():
#     await alph()
#
#
# if __name__ == "__main__":
#     asyncio.run(main())


res = subprocess.call("Rscript discover/file.R", shell=True)

res
#
# def test():
#     return "this is a test"
#
# print(test())
