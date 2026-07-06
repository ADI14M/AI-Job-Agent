import time
from fastapi import Request
from app.core.logger import system_logger

async def add_timing_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    
    # Extract path and method
    path = request.url.path
    method = request.method
    
    system_logger.info(f"PERFORMANCE: {method} {path} completed in {process_time:.4f} seconds")
    
    response.headers["X-Process-Time"] = str(process_time)
    return response
