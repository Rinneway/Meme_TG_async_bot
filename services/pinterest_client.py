import os
import logging
import random
from typing import List, Optional

from py3pin.Pinterest import Pinterest
from config import PINTEREST_EMAIL, PINTEREST_PASSWORD

logger = logging.getLogger(__name__)

pinterest_client: Optional[Pinterest] = None


def get_pinterest_client() -> Pinterest:
    """Инициализирует клиент Pinterest"""
    global pinterest_client

    if pinterest_client is None:
        if not PINTEREST_EMAIL or not PINTEREST_PASSWORD:
            raise ValueError("Pinterest credentials not set in Environment Variables")

        cred_root = "/tmp/pinterest_cookies"
        os.makedirs(cred_root, exist_ok=True)

        pinterest_client = Pinterest(
            email=PINTEREST_EMAIL,
            password=PINTEREST_PASSWORD,
            cred_root=cred_root
        )

        try:
            pinterest_client.login()
            logger.info("✅ Pinterest client initialized and logged in")
        except Exception as e:
            logger.error(f"❌ Pinterest login failed: {e}")
            raise e

    return pinterest_client


async def search_pins(query: str, limit: int = 50) -> List[dict]:
    try:
        client = get_pinterest_client()
        pins = []
        count = 0

        for pin in client.search(query=query, scope='pins'):
            if count >= limit:
                break

            # Проверяем наличие картинки
            images = pin.get('images')
            if images:
                # Берем оригинал или максимальный доступный размер
                img_url = None
                if 'orig' in images:
                    img_url = images['orig']['url']
                elif '736x' in images:
                    img_url = images['736x']['url']

                if img_url:
                    pins.append({
                        'url': img_url,
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