import asyncio

async def task(name, delay):
    await asyncio.sleep(delay)
    print(f"{name} completed")

async def main():
    await asyncio.gather(
        task("Task A", 2),
        task("Task B", 1),
    )

asyncio.run(main())