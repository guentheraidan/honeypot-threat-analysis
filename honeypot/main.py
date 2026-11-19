# Author: Aidan Guenther
"""Runs every honeypot service concurrently"""
import asyncio
from services import http_login

async def main() -> None:
    await asyncio.gather(
        http_login.serve(),
        # ftp.serve(), decoy.serve()
    )

if __name__ == "__main__":
    asyncio.run(main())