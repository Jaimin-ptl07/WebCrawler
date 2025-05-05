# WebCrawler

**WebCrawler** is a Python-based project designed to crawl and extract data from websites. It includes various scripts tailored for different crawling tasks.

## Features

- **Website Crawling**: Navigate through web pages to collect data.
- **Government Website Crawler**: Specialized script for crawling government websites.
- **Demo and Test Crawls**: Scripts to demonstrate and test crawling functionalities.
- **Data Storage**: Crawled data is stored in the `crawled_data` directory.

## Project Structure

- `websiteCrawl.py`: Main script for crawling websites.
- `gov crawler.py`: Script specialized for crawling government websites.
- `democrawl.py`: Demonstration script showcasing crawling capabilities.
- `test crawl.py`: Script for testing crawling functions.
- `crawled_data/`: Directory where the crawled data is stored.

## Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Jaimin-ptl07/WebCrawler.git
   cd WebCrawler
   ```

2. **Create a virtual environment** (optional but recommended):

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install required dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

   *Note: Ensure that a `requirements.txt` file is present with the necessary dependencies.*

## Usage

Run the desired crawler script:

```bash
python websiteCrawl.py
```

Replace `websiteCrawl.py` with the script you wish to execute, such as `gov crawler.py` or `democrawl.py`.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request for any enhancements or bug fixes.

## License

This project is open-source and available under the [MIT License](LICENSE).

## Acknowledgments

- Developed by [Jaimin Patel](https://github.com/Jaimin-ptl07)
