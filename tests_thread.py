from concurrent.futures import ThreadPoolExecutor, as_completed, wait
import time


def thread_function(context):
    print(f"Function context: {context}")
    context[f"fn{context['index']}_val"] = context["index"] + 1
    time.sleep(1)
    print(f"Function context: {context}")
    return context


def main():
    threads = ThreadPoolExecutor(4, "ctb")
    context = {"init": "starting context"}
    results = {
        threads.submit(thread_function, {**context, "index": i}): i for i in range(5)
    }

    # for future in as_completed(results):
    #     name = results[future]
    #     try:
    #         result = future.result()
    #         context = {**context, **result}
    #         print(f"Thread {name} returned: {result}")
    #     except Exception as e:
    #         print(f"Thread {name} raised an exception: {e}")

    futures, _ = wait(results)
    for future in futures:
        name = results[future]
        try:
            result = future.result()
            context = {**context, **result}
            print(f"Thread {name} returned: {result}")
        except Exception as e:
            print(f"Thread {name} raised an exception: {e}")

    print(f"Context:", context)


if __name__ == "__main__":
    main()
