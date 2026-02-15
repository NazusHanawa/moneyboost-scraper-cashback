import time
import functools

from config import DEBUG

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        
        duration = end_time - start_time
        if DEBUG:
            print(f"⏱️ '{func.__name__}': {duration:.4f} seconds")
        return result
    return wrapper

class MockResponse:
    def __init__(self, text):
        self.text = text