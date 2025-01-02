# Indeed Job Posting and Company Reviews Scraper and Recommender System

## Overview

This tool scrapes job postings and company reviews from Indeed and then uses the data to recommend job opportunities based on user preferences and your resume. The system is built with Playwright for scraping and leverages the ChatGPT API for generating insights and recommendations.

## Requirements

- **Playwright**: You must install Playwright to enable browser automation for scraping. Used to get around popup and anti-scrape programs
- **Beautiful Soup**: Used to scrape the localized downloaded pages from Playwright
- **ChatGPT API Key**: A personal secret key from the ChatGPT API is required to process and analyze the scraped content.

## Setup

1. Install Playwright:
   ```bash
   pip install playwright
   playwright install
