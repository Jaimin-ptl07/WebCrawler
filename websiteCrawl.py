import asyncio
import os
import json
from urllib.parse import urljoin, urlparse
from collections import deque
import aiohttp
from aiofiles import open as aio_open
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.async_dispatcher import MemoryAdaptiveDispatcher
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

# Directory to save crawled data
DATA_DIR = "crawled_data"
os.makedirs(DATA_DIR, exist_ok=True)

async def download_media(session, media_url, media_dir):
    """Download media files asynchronously."""
    try:
        async with session.get(media_url) as response:
            if response.status == 200:
                media_filename = os.path.join(media_dir, os.path.basename(media_url))
                async with aio_open(media_filename, "wb") as f:
                    await f.write(await response.read())
                print(f"Downloaded media: {media_filename}")
            else:
                print(f"Failed to download {media_url}: Status {response.status}")
    except Exception as e:
        print(f"Error downloading {media_url}: {e}")

async def save_page_data(crawler, result):
    """Save the crawled page data to files."""
    if not result.success:
        print(f"Failed to crawl: {result.url} - {result.error_message}")
        return

    # Create a directory for the current URL
    url_path = urlparse(result.url).path.strip("/").replace("/", "_")
    page_dir = os.path.join(DATA_DIR, url_path)
    os.makedirs(page_dir, exist_ok=True)

    # Save cleaned HTML
    if result.cleaned_html:
        with open(os.path.join(page_dir, "cleaned.html"), "w", encoding="utf-8") as f:
            f.write(result.cleaned_html)

    # Save markdown
    if result.markdown:
        markdown_content = result.markdown
        if isinstance(markdown_content, dict) and 'raw_markdown' in markdown_content:
            markdown_content = markdown_content['raw_markdown']
        with open(os.path.join(page_dir, "content.md"), "w", encoding="utf-8") as f:
            f.write(markdown_content)

    # Save metadata
    if result.metadata:
        with open(os.path.join(page_dir, "metadata.json"), "w", encoding="utf-8") as f:
            json.dump(result.metadata, f, ensure_ascii=False, indent=4)

    # Download media files
    async with aiohttp.ClientSession() as session:
        for media_type, media_list in result.media.items():
            media_dir = os.path.join(page_dir, media_type)
            os.makedirs(media_dir, exist_ok=True)
            tasks = []
            for media in media_list:
                media_url = media.get('src')
                if media_url:
                    tasks.append(download_media(session, media_url, media_dir))
            await asyncio.gather(*tasks)

async def crawl_website(start_url, max_depth=2):
    # Browser configuration
    browser_config = BrowserConfig(
        headless=True,
        verbose=True,
        accept_downloads=True
    )

    # Crawler run configuration
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=DefaultMarkdownGenerator(),
        process_iframes=True,
        remove_overlay_elements=True,
        pdf=True,
        screenshot=True,
        word_count_threshold=10,
        excluded_tags=['form', 'header', 'footer', 'nav'],
        exclude_external_links=True,
        exclude_social_media_links=True,
        exclude_domains=["ads.com", "spammytrackers.net"],
        exclude_external_images=True
    )

    # Dispatcher configuration
    dispatcher = MemoryAdaptiveDispatcher(
        memory_threshold_percent=70.0,
        check_interval=1.0,
        max_session_permit=5
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        queue = deque([(start_url, 0)])
        visited = set()

        while queue:
            current_url, depth = queue.popleft()
            if depth > max_depth or current_url in visited:
                continue

            visited.add(current_url)
            result = await crawler.arun(url=current_url, config=run_config)
            await save_page_data(crawler, result)

            if result.success:
                new_urls = []
                for link_type in ['internal', 'external']:
                    for link in result.links.get(link_type, []):
                        href = link.get('href')
                        if href:
                            next_url = urljoin(current_url, href)
                            if next_url not in visited:
                                new_urls.append((next_url, depth + 1))

                if new_urls:
                    results = await crawler.arun_many(
                        urls=[url for url, _ in new_urls],
                        config=run_config,
                        dispatcher=dispatcher
                    )

                    for res in results:
                        await save_page_data(crawler, res)
                        if res.success:
                            for link_type in ['internal', 'external']:
                                for link in res.links.get(link_type, []):
                                    href = link.get('href')
                                    if href:
                                        next_url = urljoin(res.url, href)
                                        if next_url not in visited:
                                            queue.append((next_url, depth + 2))

if __name__ == "__main__":
    start_url = "https://www.ril.com"
    asyncio.run(crawl_website(start_url))
