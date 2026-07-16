import asyncio

import enka


UID = 862735734


async def main():
    async with enka.GenshinClient(
        enka.gi.Language.JAPANESE
    ) as client:

        showcase = await client.fetch_showcase(UID)
        player = showcase.player

        print("=== フィールド名 ===")

        for key in player.__dict__:
            print(key)


asyncio.run(main())