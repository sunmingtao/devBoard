import asyncio

sem = asyncio.Semaphore(2)  # 最多允许2个并发

async def task(n):
    async with sem:
        print(f"Task {n} started")
        await asyncio.sleep(1)
        print(f"Task {n} completed")

async def main():
    await asyncio.gather(*(task(i) for i in range(5)))

asyncio.run(main())