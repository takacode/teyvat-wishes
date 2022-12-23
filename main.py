import argparse
import asyncio
import logging
import os
import pathlib
import pytz
from dotenv import load_dotenv
from datetime import datetime

import genshin
import jinja2

logger = logging.getLogger()
load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("-t", "--template", default="template.html", type=pathlib.Path)
parser.add_argument("-o", "--output", default="stats.html", type=pathlib.Path)
parser.add_argument("-c", "--cookies", default=None)
parser.add_argument("-l", "--lang", "--language", choices=genshin.LANGS, default="en-us")

def format_date(date: "datetime"):
    tz = pytz.timezone("Asia/Singapore")
    now = date.now(tz=tz)
    fmt = f"{now.strftime('%b')} \
            {now.strftime('%d')}, \
            {now.strftime('%Y')} \
            {now.strftime('%H:%M %z')}"
    return fmt

async def main():
    args = parser.parse_args()
    wish_link = os.getenv("WISH_LINK")
    auth_key = genshin.utility.extract_authkey(wish_link)

    client = genshin.Client(authkey = auth_key, debug=False, game=genshin.Game.GENSHIN)
    character_banner_history = await client.wish_history([301], limit=200).flatten()
    weapon_banner_history = await client.wish_history([302], limit=200).flatten()
    permanent_banner_history = await client.wish_history([200], limit=200).flatten()

    template: jinja2.Template = jinja2.Template(args.template.read_text())
    rendered = template.render(
        lang=args.lang,
        character_banner_history=character_banner_history,
        weapon_banner_history=weapon_banner_history,
        permanent_banner_history = permanent_banner_history,
        updated_at=format_date(datetime.now()),
        _int=int
    )
    args.output.write_text(rendered)


if __name__ == "__main__":
    asyncio.run(main())