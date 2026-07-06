import time
import functools
from app.core.logger import system_logger

class RetryManager:
    @staticmethod
    def with_retries(max_retries=3, base_delay=2, max_delay=30):
        """
        Exponential backoff decorator for browser automation actions.
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                retries = 0
                delay = base_delay
                while retries < max_retries:
                    try:
                        return func(*args, **kwargs)
                    except Exception as e:
                        retries += 1
                        if retries >= max_retries:
                            system_logger.error(f"Function {func.__name__} failed after {max_retries} retries: {e}")
                            raise e
                        
                        system_logger.warning(f"Function {func.__name__} failed: {e}. Retrying in {delay}s...")
                        time.sleep(delay)
                        delay = min(delay * 2, max_delay)
            return wrapper
        return decorator
