import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator

async def crawl_ril():
    # Browser configuration
    browser_config = BrowserConfig(
        headless=True,  # Run browser in headless mode
        verbose=True,   # Enable verbose logging
        accept_downloads=True  # Enable downloading of files
    )

    # Crawler run configuration
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,  # Bypass cache to fetch fresh content
        markdown_generator=DefaultMarkdownGenerator(),
        process_iframes=True,         # Process content within iframes
        remove_overlay_elements=True, # Remove overlay elements for cleaner extraction
        pdf=True,                     # Generate PDF of the page
        screenshot=True               # Capture screenshot of the page
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Crawl the RIL homepage
        result = await crawler.arun(
            url="https://www.ril.com",
            config=run_config
        )

        if result.success:
            # Print the final URL crawled
            print(f"Final URL: {result.url}")

            # Print the length of the raw HTML content
            print(f"HTML content length: {len(result.html)}")

            # Print the first 500 characters of the cleaned HTML content
            if result.cleaned_html:
                print(f"Cleaned HTML preview: {result.cleaned_html[:500]}")

            # Print the first 500 characters of the extracted markdown content
            if result.markdown:
                print(f"Markdown content preview: {result.markdown[:500]}")

            # Print metadata
            if result.metadata:
                print("Metadata:")
                for key, value in result.metadata.items():
                    print(f"  {key}: {value}")

            # Print internal and external links
            if result.links:
                print("Internal Links:")
                for link in result.links.get("internal", []):
                    print(f"  {link['href']}")
                print("External Links:")
                for link in result.links.get("external", []):
                    print(f"  {link['href']}")

            # Print media files
            if result.media:
                print("Images:")
                for image in result.media.get("images", []):
                    print(f"  {image['src']}")
                print("Videos:")
                for video in result.media.get("videos", []):
                    print(f"  {video['src']}")
            # List downloaded files
            if result.downloaded_files:
                print("Downloaded Files:")
                for file_path in result.downloaded_files:
                    print(f"  {file_path}")

            # Save screenshot if available
            if result.screenshot:
                with open("ril_screenshot.png", "wb") as f:
                    f.write(result.screenshot)
                print("Screenshot saved as ril_screenshot.png")

            # Save PDF if available
            if result.pdf:
                with open("ril_page.pdf", "wb") as f:
                    f.write(result.pdf)
                print("PDF saved as ril_page.pdf")

            # Print extracted content
            if result.extracted_content:
                print(f"Extracted Content: {result.extracted_content}")

            # Print response headers
            if result.response_headers:
                print("Response Headers:")
                for key, value in result.response_headers.items():
                    print(f"  {key}: {value}")

            # Print HTTP status code
            if result.status_code:
                print(f"Status Code: {result.status_code}")

            # Print SSL certificate information
            if result.ssl_certificate:
                print("SSL Certificate:")
                print(f"  Subject: {result.ssl_certificate.subject}")
                print(f"  Issuer: {result.ssl_certificate.issuer}")
                print(f"  Valid From: {result.ssl_certificate.valid_from}")
                print(f"  Valid To: {result.ssl_certificate.valid_to}")

        else:
            print(f"Crawl failed: {result.error_message}")

if __name__ == "__main__":
    asyncio.run(crawl_ril())
