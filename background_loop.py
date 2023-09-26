from event_related import *


def start_background_loop(task_queue):
    # task_queue = []#(timestamp, func, args, kwargs, is_async)
    while True:
        if task_queue:
            task_queue.sort(key=lambda x: x[0])
            

            task = task_queue.pop(0)
            if task[0] <= time.time():
                if task[4]:
                    asyncio.run_coroutine_threadsafe(task[1](*task[2], **task[3]), client.loop) # runs the task in the background
                else:
                    task[1](*task[2], **task[3])
        time.sleep(1)
        