"""Fetch text from NCBI's E-utilities inside a web browser (for this course page).

On your own computer, use Biopython's Bio.Entrez instead (see Lesson 12).
If NCBI can't be reached (offline, blocked, or too many requests), this
module uses a saved copy of the answer that comes with the page.
"""
import asyncio
import time

from pyodide.http import pyfetch

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
TOOL_NAME = "pfb_course_level2"      # tells NCBI which program is asking
SECONDS_BETWEEN_REQUESTS = 0.4       # NCBI allows at most 3 requests per second without an API key
SAVED_ON = "3 October 2026"

_last_request = [0.0]


async def fetch_text(url, saved_copy):
    """Return NCBI's answer for url as text, or the saved copy if NCBI can't be reached."""
    wait = SECONDS_BETWEEN_REQUESTS - (time.monotonic() - _last_request[0])
    if wait > 0:
        await asyncio.sleep(wait)        # be polite: never more than ~3 requests per second
    _last_request[0] = time.monotonic()
    try:
        response = await pyfetch(url)
        if not response.ok:
            raise OSError(f"NCBI answered with status {response.status}")
        text = await response.string()
        print("🌐 Live answer from NCBI.")
        return text
    except Exception as error:
        print(f"📦 NCBI couldn't be reached just now ({error}).")
        print(f"   No problem: using the saved copy {saved_copy!r} (saved on {SAVED_ON}).")
        print("   Your code works the same way; only the source of the text is different.")
        with open(saved_copy) as f:
            return f.read()
