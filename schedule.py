import asyncio

from broker import schedule

async def main():
    schedule_id = await schedule()
    
    print(f"Schedule ID: {schedule_id}")

asyncio.run(main())
