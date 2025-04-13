import scrapy
import re
from datetime import datetime
import logging # Import logging

# Define a Scrapy Item for structured data (optional but good practice)
class GithubRepoItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field() # Keep name separate for logic
    about = scrapy.Field()
    last_updated = scrapy.Field()
    languages = scrapy.Field()
    num_commits = scrapy.Field()


class GithubReposSpider(scrapy.Spider):
    name = 'github_repos'
    allowed_domains = ['github.com']
    # Base URL, username will be appended in start_requests
    base_url = 'https://github.com/{}?tab=repositories'

    # Custom settings for XML output and logging
    custom_settings = {
        'FEEDS': {
            'repositories.xml': {
                'format': 'xml',
                'encoding': 'utf8',
                'item_classes': ['github_scraper.spiders.github_repos_spider.GithubRepoItem'], # Adjust path if needed
                'indent': 4,
                'overwrite': True, # Overwrite the file if it exists
            },
        },
        'LOG_LEVEL': 'INFO', # Set log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        # Add delay and concurrency settings to be polite to GitHub
        'DOWNLOAD_DELAY': 1, # Add a 1-second delay between requests
        'CONCURRENT_REQUESTS_PER_DOMAIN': 8, # Limit concurrent requests
        'AUTOTHROTTLE_ENABLED': True, # Enable AutoThrottle extension
        'AUTOTHROTTLE_TARGET_CONCURRENCY': 1.0, # Adjust based on testing
    }

    def __init__(self, username=None, *args, **kwargs):
        super(GithubReposSpider, self).__init__(*args, **kwargs)
        if username is None:
            raise ValueError("Please provide a GitHub username using -a username=YOUR_USERNAME")
        self.start_urls = [self.base_url.format(username)]
        self.username = username
        logging.info(f"Starting scrape for user: {self.username}") # Use logging

    def parse(self, response):
        """
        Parses the main repositories page.
        Extracts basic info and yields requests to individual repo pages.
        """
        # Selector for the list containing repositories
        repo_list_selector = 'ul[data-filterable-for="your-repos-filter"] > li'
        # Fallback selector if the primary one doesn't work (GitHub structure might change)
        if not response.css(repo_list_selector):
             repo_list_selector = '#user-repositories-list > ul > li' # Older potential structure

        repos = response.css(repo_list_selector)
        logging.info(f"Found {len(repos)} potential repository entries on main page.") # Use logging

        if not repos:
             logging.warning(f"Could not find repository list for user {self.username} on {response.url}. Check selectors or if the profile/repositories are public.") # Use logging
             return # Stop if no repos found

        for repo in repos:
            repo_name = repo.css('div[class*="col-"] h3 a ::text').get()
            # Sometimes the repo name might have extra whitespace or be split
            if repo_name:
                repo_name = repo_name.strip()
            else:
                # Try alternative selector if the primary one fails
                repo_name_alt = repo.css('h3 a ::text').get()
                if repo_name_alt:
                    repo_name = repo_name_alt.strip()

            if not repo_name:
                 logging.warning(f"Could not extract repo name from an entry: {repo.get()}") # Use logging
                 continue # Skip this entry if name is not found

            repo_relative_url = repo.css('div[class*="col-"] h3 a ::attr(href)').get()
             # Try alternative selector if the primary one fails
            if not repo_relative_url:
                repo_relative_url = repo.css('h3 a ::attr(href)').get()

            if not repo_relative_url:
                logging.warning(f"Could not extract repo URL for repo: {repo_name}") # Use logging
                continue # Skip if URL is not found

            repo_url = response.urljoin(repo_relative_url)

            # Extract About description
            about = repo.css('p[itemprop="description"] ::text').get()
            if about:
                about = about.strip()
            else:
                about = None # Explicitly set to None if empty

            # Extract Last Updated timestamp
            last_updated_raw = repo.css('relative-time ::attr(datetime)').get()
            last_updated = None
            if last_updated_raw:
                try:
                     # Parse the ISO 8601 timestamp
                    last_updated = datetime.fromisoformat(last_updated_raw.replace('Z', '+00:00')).isoformat()
                except ValueError:
                    logging.warning(f"Could not parse timestamp '{last_updated_raw}' for repo: {repo_name}") # Use logging
                    last_updated = last_updated_raw # Keep raw string if parsing fails

            # Create initial data dictionary to pass to the next request
            initial_data = {
                'url': repo_url,
                'name': repo_name,
                'about': about,
                'last_updated': last_updated,
            }

            # Yield a request to the individual repository page to get languages and commit count
            yield scrapy.Request(
                url=repo_url,
                callback=self.parse_repo_page,
                cb_kwargs={'initial_data': initial_data} # Pass initial data
            )

        # --- Handle Pagination ---
        # Find the 'Next' button link
        next_page = response.css('a.next_page ::attr(href)').get()
        # Alternative selector for pagination if the first one fails
        if not next_page:
            next_page = response.xpath('//a[@rel="next" and contains(text(), "Next")]/@href').get()

        if next_page is not None:
            next_page_url = response.urljoin(next_page)
            logging.info(f"Following pagination link to: {next_page_url}") # Use logging
            yield scrapy.Request(next_page_url, callback=self.parse)


    def parse_repo_page(self, response, initial_data):
        """
        Parses the individual repository page.
        Extracts languages, commit count, and finalizes the 'About' field.
        """
        item = GithubRepoItem() # Create the item instance
        item['url'] = initial_data['url']
        item['last_updated'] = initial_data['last_updated']
        # Use the initial name field for logic, but don't include it in the final output item
        repo_name = initial_data['name']
        final_about = initial_data['about'] # Start with the 'about' from the list page

        # --- Check if repository is empty ---
        # Common indicators of an empty repo (selectors might change)
        is_empty_message = response.css('h3:contains("Get started by creating a new file")').get() or \
                           response.css('h2:contains("Quick setup")').get() or \
                           response.css('div.blankslate h3:contains("Get started")').get() # Add more checks if needed
        # Another check: absence of the commit link/count element
        commit_link = response.css('a[href*="/commits/"] strong ::text').get() or \
                      response.css('ul.list-style-none > li > a[href*="/commits/"] strong ::text').get() # Find commit count element

        is_empty = bool(is_empty_message) or not bool(commit_link)
        # Add more robust checks if needed, e.g., check file count if available

        if is_empty:
            logging.info(f"Repository '{repo_name}' appears to be empty.") # Use logging
            item['languages'] = None
            item['num_commits'] = None
            # Keep the 'about' found on the list page (even if None) for empty repos
            item['about'] = final_about
        else:
            # --- Extract Languages (if not empty) ---
            languages = {}
            lang_elements = response.css('div[data-view-component="true"] h2:contains("Languages") + ul > li') # Updated selector
            if not lang_elements:
                 # Fallback selector (might be older structure or change)
                 lang_elements = response.css('.BorderGrid-row:contains("Languages") .BorderGrid-cell ul li')

            for lang_item in lang_elements:
                lang_name = lang_item.css('span:first-child ::text').get()
                lang_percent = lang_item.css('span:last-child ::text').get()
                if lang_name and lang_percent:
                    languages[lang_name.strip()] = lang_percent.strip()
            item['languages'] = languages if languages else None # Set to None if no languages found

            # --- Extract Number of Commits (if not empty) ---
            # Try to find the commit count, often linked to the commit history
            commits_text = commit_link # Use the text found earlier
            if not commits_text: # Try another common selector structure if the first failed
                commits_text = response.css('.numbers-summary li:contains("commit") a span strong ::text').get()

            num_commits = None
            if commits_text:
                # Extract numbers, remove commas
                match = re.search(r'([\d,]+)', commits_text.replace(',', ''))
                if match:
                    try:
                        num_commits = int(match.group(1))
                    except ValueError:
                        logging.warning(f"Could not convert commit text '{commits_text}' to int for repo: {repo_name}") # Use logging
                        num_commits = None # Set to None if conversion fails
                else:
                    logging.warning(f"Could not extract commit number from text: '{commits_text}' for repo: {repo_name}") # Use logging
            else:
                 logging.warning(f"Could not find commit count element for non-empty repo: {repo_name}") # Use logging

            item['num_commits'] = num_commits

            # --- Handle 'About' logic for non-empty repos ---
            # If the 'about' extracted from the list page was empty/None, use the repo name.
            if final_about is None:
                final_about = repo_name
                logging.info(f"Using repo name '{repo_name}' as About for non-empty repo with no description.") # Use logging

            item['about'] = final_about

        # Yield the completed item
        yield item