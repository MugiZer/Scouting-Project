import asyncio
import sys
import uvicorn

def main():
    if sys.platform == "win32":
        # Force ProactorEventLoop
        loop = asyncio.WindowsProactorEventLoopPolicy().new_event_loop()
        asyncio.set_event_loop(loop)
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    
    # Start uvicorn without reload to avoid subprocesses losing loop policy
    print("Starting server with Windows Proactor fix enabled...")
    uvicorn.run(
        "a:app", 
        host="127.0.0.1", 
        port=8000, 
        reload=False, # DISABLED to fix 'NotImplementedError'
        loop="asyncio"
    )

if __name__ == "__main__":
    main()
