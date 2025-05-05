import asyncio
from crawl4ai import AsyncWebCrawler
from pymongo import MongoClient
from lxml import html
from urllib.parse import urljoin
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import time

# MongoDB configuration
MONGO_URI = "mongodb://localhost:27017"
DATABASE_NAME = "web_crawler"
CHILD_PAGES_COLLECTION = "child_pages"
PAGE_METADATA_COLLECTION = "page_metadata"

# Initialize MongoDB client
client = MongoClient(MONGO_URI)
db = client[DATABASE_NAME]
child_pages_collection = db[CHILD_PAGES_COLLECTION]
page_metadata_collection = db[PAGE_METADATA_COLLECTION]

# File extensions for documents and images
DOCUMENT_EXTENSIONS = ('.pdf', '.pptx', '.xls', '.xlsx', '.doc', '.docx', '.zip')
IMAGE_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg')

# Global rate-limiting variable
last_request_time = 0


async def rate_limited_request():
    """
    Ensures 1 request per second.
    """
    global last_request_time
    elapsed_time = time.time() - last_request_time
    if elapsed_time < 1:
        await asyncio.sleep(1 - elapsed_time)
    last_request_time = time.time()


async def crawl_and_store(url, crawler, visited_urls):
    """
    Crawls a URL, stores document and image links in `page_metadata`, and other links in `child_pages`.
    """
    if url in visited_urls:
        return []  # Avoid duplicate processing and return an empty list

    visited_urls.add(url)
    await rate_limited_request()  # Respect rate-limiting

    try:
        result = await crawler.arun(url=url)
        if result.cleaned_html is None:
            raise ValueError("Cleaned HTML is None for URL: " + url)

        success = result.success
        status_code = result.status_code

        # Parse cleaned HTML
        tree = html.fromstring(result.cleaned_html)

        # Extract all links and images
        all_links = tree.xpath("//a/@href")
        all_links = [link for link in all_links if link]  # Filter out None values
        all_images = tree.xpath("//img/@src")  # Extract image URLs

        # Separate document links and other links
        document_links = [
            urljoin(url, link) for link in all_links
            if any(link.endswith(ext) for ext in DOCUMENT_EXTENSIONS)
        ]
        non_document_links = [
            urljoin(url, link) for link in all_links
            if not any(link.endswith(ext) for ext in DOCUMENT_EXTENSIONS)
        ]

        # Process images
        image_links = [
            urljoin(url, img) for img in all_images
            if any(img.endswith(ext) for ext in IMAGE_EXTENSIONS)
        ]

        # Store document and image links in `page_metadata`
        if document_links or image_links:
            metadata = {
                "url": url,
                "document_links": document_links,
                "image_links": image_links,
                "fetched_at": datetime.utcnow().isoformat()
            }
            page_metadata_collection.insert_one(metadata)
            print(f"Stored metadata for: {url} with documents: {document_links} and images: {image_links}")

        # Store non-document links in `child_pages`
        for link in non_document_links:
            child_page_data = {
                "url": link,
                "success": success,
                "status_code": status_code,
                "error": None,
                "fetched_at": datetime.utcnow().isoformat()
            }
            child_pages_collection.insert_one(child_page_data)
            print(f"Stored child page information for: {link}")

        # Return non-document links for further crawling
        return non_document_links
    except Exception as e:
        # Log failures in `child_pages` collection
        child_page_data = {
            "url": url,
            "success": False,
            "status_code": None,
            "error": str(e),
            "fetched_at": datetime.utcnow().isoformat()
        }
        child_pages_collection.insert_one(child_page_data)
        print(f"Failed to fetch {url}: {e}")
        return []  # Return an empty list on failure


def process_domain(url, visited_urls):
    """
    Processes a .gov.in domain in a separate thread.
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(main_threaded(url, visited_urls))


async def main_threaded(start_url, visited_urls):
    """
    Handles crawling within a thread for a specific domain.
    """
    urls_to_crawl = [start_url]
    async with AsyncWebCrawler() as crawler:
        while urls_to_crawl:
            current_url = urls_to_crawl.pop(0)
            child_links = await crawl_and_store(current_url, crawler, visited_urls)
            for link in child_links:
                if link not in visited_urls and link.endswith(".gov.in"):
                    urls_to_crawl.append(link)


async def main():
    start_url = "https://igod.gov.in/"
    visited_urls = set()

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.submit(process_domain, start_url, visited_urls)


if __name__ == "__main__":
    asyncio.run(main())
