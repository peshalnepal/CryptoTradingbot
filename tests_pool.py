import multiprocessing
from multiprocess.pool import Pool
from functools import partial


def func(args):
    return args


def process(args):
    print("Input:", args)
    return func(args)


if __name__ == "__main__":
    pool: Pool = multiprocessing.Pool()

    # Define kwargs
    kwargs = [[2], [3], [4]]

    # Create a partial function with kwargs applied

    # Use starmap with partial function
    results = pool.starmap(process, kwargs)

    print(results)

    pool.close()
    pool.join()
