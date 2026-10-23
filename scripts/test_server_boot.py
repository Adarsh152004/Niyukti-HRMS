import asyncio
import sys
sys.path.insert(0, ".")

async def boot():
    print("Step 1: importing app")
    from backend.app import app
    print("Step 2: app imported successfully!")
    from backend.runtime.kernel import EnterpriseKernel
    kernel = EnterpriseKernel.get_instance()
    print("Step 3: starting kernel...")
    await kernel.start()
    print("Step 4: kernel started!")
    from backend.events.outbox.worker import outbox_worker
    print("Step 5: starting outbox_worker...")
    await outbox_worker.start()
    print("Step 6: outbox_worker started!")

if __name__ == "__main__":
    asyncio.run(boot())
