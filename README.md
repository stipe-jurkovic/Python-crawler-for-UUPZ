# Njuškalo Web Scraper

This project is a Python-based web scraper specifically designed for the "Njuškalo" website. It has been developed as part of the "Uvod u podatkovnu znanost" (Introduction to Data Science) class.

## Overview

The Njuškalo web scraper allows users to extract data from the Njuškalo website, which is a popular online marketplace in Croatia. By leveraging the power of web scraping, this tool enables users to gather valuable information such as product listings, prices, descriptions, and more.

## Features

- Easy-to-use interface for specifying search criteria and filters
- Efficient data extraction using web scraping techniques
- Customizable output formats (e.g., CSV, JSON)
- Support for handling pagination and multiple result pages
- Error handling and robustness to handle various scenarios

## Installation

To use the Njuškalo web scraper, follow these steps:

1. Clone the repository: `git clone https://github.com/your-username/your-repo.git`
2. Install the required dependencies: `pip install -r requirements.txt`
3. Run the scraper: `python scraper.py`

## Usage

1. Specify your search criteria and filters in the `config.json` file.
2. Run the scraper using the command mentioned in the installation section.
3. The scraped data will be saved in the specified output format and location.

## Contributing

Contributions are welcome! If you have any suggestions, bug reports, or feature requests, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Dictionary

- **Building floor location - key**:
    - Prizemlje: 0
    - Suteren: 0
    - Visoko prizemlje: 1
    - Potkrovlje: average_floor+1
    - Visoko potkrovlje: average_floor+2
    - Penthouse: average_floor+3

- **Type of property - key**:
    - U stambenoj zgradi: 0
    - U kući: 1