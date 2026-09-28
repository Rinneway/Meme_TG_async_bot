import logging
import random
from typing import List, Optional

from py3pin.Pinterest import Pinterest
from config import PINTEREST_EMAIL, PINTEREST_PASSWORD, PINTEREST_CSRFTOKEN, PINTEREST_SESSION

logger = logging.getLogger(__name__)

pinterest_client: Optional[Pinterest] = None


def get_pinterest_client() -> Pinterest:
    global pinterest_client

    if pinterest_client is None:
        # Пробуем через cookies (надёжнее)
        if PINTEREST_CSRFTOKEN and PINTEREST_SESSION:
            pinterest_client = Pinterest(
                email=PINTEREST_EMAIL,
                password=PINTEREST_PASSWORD,
                cred_root="pinterest_cookies"  # папка для хранения cookies
            )
            pinterest_client.login()
            logger.info("✅ Pinterest client initialized with cookies")
        elif PINTEREST_EMAIL and PINTEREST_PASSWORD:
            pinterest_client = Pinterest(
                email=PINTEREST_EMAIL,
                password=PINTEREST_PASSWORD
            )
            pinterest_client.login()
            logger.info("✅ Pinterest client initialized with email/password")
        else:
            raise ValueError("Pinterest credentials not set")

    return pinterest_client


async def search_pins(query: str, limit: int = 50) -> List[dict]:
    try:
        client = get_pinterest_client()
        pins = []
        count = 0

        for pin in client.search(query=query, scope='pins'):
            if count >= limit:
                break

            if pin.get('images') and pin['images'].get('orig'):
                pins.append({
                    'url': pin['images']['orig']['url'],
                    'id': pin.get('id'),
                    'description': pin.get('description', '')
                })
            count += 1

        logger.info(f"Found {len(pins)} pins for query: {query}")
        return pins

    except Exception as e:
        logger.error(f"Pinterest search error: {e}")
        return []


async def get_random_pin(query: str) -> Optional[dict]:
    pins = await search_pins(query, limit=50)
    if not pins:
        return None
    return random.choice(pins)