import asyncio
import enka


async def fetch_profile(uid: int):
    async with enka.GenshinClient() as client:
        showcase = await client.fetch_showcase(uid)
        return showcase


def get_profile(uid: int):
    return asyncio.run(fetch_profile(uid))