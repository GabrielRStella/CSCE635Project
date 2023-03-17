import asyncio
import random

things_to_schedule = []
global_promises = []
def asyncify(interval=None):
    if interval != None:
        import time
        def outer_wrapper(function_being_wrapped):
            @asyncify()
            async def interval_wrapper():
                prev_execution_time = time.time() - interval
                while True:
                    duration = interval - (time.time() - prev_execution_time)
                    if duration > 0:
                        await asyncio.sleep(duration)
                    prev_execution_time = time.time()
                    await function_being_wrapped()
            try:
                task = interval_wrapper()
            except RuntimeError as error:
                things_to_schedule.append(interval_wrapper)
            interval_wrapper.output = lambda *args: None
            def cancel_early():
                things_to_schedule.remove(interval_wrapper)
            interval_wrapper.output.cancel = cancel_early
        
        return outer_wrapper
    
    def outer_wrapper(function_being_wrapped):
        def double_wrapper(*args, **kwargs):
            # Half of this is probably redundant/unnecessary
            function_call_id = random.random()
            global_promises.append(function_call_id)
            async def wrapper():
                coroutine_placeholder = function_being_wrapped(*args, **kwargs)
                task = asyncio.create_task(coroutine_placeholder)
                def done_callback(arg):
                    wrapper.output = arg
                    wrapper.is_done = True
                task.add_done_callback(done_callback)
                # can't await task because "RuntimeError: cannot reuse already awaited coroutine"
                while not wrapper.is_done:
                    await asyncio.sleep(0.1)
                output = wrapper.output
                global_promises.remove(function_call_id)
                return output
            
            wrapper.is_done = False
            task = asyncio.create_task(wrapper())
            def then(function_being_wrapped):
                def inner(*args, **kwargs):
                    function_being_wrapped(wrapper.output.result())
                    return task
                task.add_done_callback(inner)
                return inner
            
            task.then = then
            return task
        
        return double_wrapper
    
    return outer_wrapper

def main(function_being_wrapped):
    async def main_wrapper(*args, **kwargs):
        for each in things_to_schedule:
            task = each()
            # update the cancel function
            each.output.cancel = lambda *args: task.cancel()
        
        await function_being_wrapped(*args, **kwargs)
        while len(global_promises) > 0:
            await asyncio.sleep(1)
    
    asyncio.run(main_wrapper())
