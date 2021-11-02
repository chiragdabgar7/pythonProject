import asyncio


async def main():
    print("chirag")
    await foo('txt')
    print("finished")


async def foo(text):
    print(text)
    await asyncio.sleep(1)

asyncio.run(main())