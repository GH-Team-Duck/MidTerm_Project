# -*- coding: utf-8 -*-
"""Github-topic-scraping-project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1yUEAWN6CULOnT9LYjaIZg2pr3wi0hCoY
"""

from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
import os
import re
from xml.etree.ElementTree import Element, SubElement, tostring
from xml.dom import minidom


GITHUB_TOKEN = ''

def get_headers():
    headers = {
        'User-Agent': 'Mozilla/5.0'
    }
    if GITHUB_TOKEN:
        headers['Authorization'] = f'token {GITHUB_TOKEN}'
    return headers

def parse_star_count(star_str):
    star_str = star_str.strip()
    if star_str[-1].lower() == 'k':
        return int(float(star_str[:-1]) * 1000)
    return int(star_str.replace(',', ''))

def get_commit_count(username, reponame):
    """Get the total number of commits via GitHub API"""
    try:
        api_url = f"https://api.github.com/repos/{username}/{reponame}/commits?per_page=1"
        response = requests.get(api_url, headers=get_headers())
        if response.status_code == 200:
            # Check for pagination in Link header
            if 'Link' in response.headers:
                match = re.search(r'&page=(\d+)>; rel="last"', response.headers['Link'])
                if match:
                    return match.group(1)
            else:
                return "1"  # Only 1 commit, no pagination
        else:
            print(f"GitHub API commit count failed for {username}/{reponame}: {response.status_code}")
    except Exception as e:
        print(f"Error fetching commit count for {username}/{reponame}: {e}")
    return ""

def get_repo_info(h3_tag, star_tag):
    """Get detailed info about a repository"""
    try:
        atags = h3_tag.find_all('a')
        username = atags[0].text.strip()
        reponame = atags[1].text.strip()
        repo_path = atags[1]['href']
        repo_url = "https://www.github.com" + repo_path
        stars = parse_star_count(star_tag.text.strip())

        repo_response = requests.get(repo_url, headers=get_headers())
        if repo_response.status_code != 200:
            return username, reponame, repo_url, stars, "", "", "", ""

        repo_soup = BeautifulSoup(repo_response.text, 'html.parser')

        # About
        about_tag = repo_soup.find('p', {'class': 'f4 my-3'})
        about = about_tag.text.strip() if about_tag else ""

        # Last Updated
        rel_time_tag = repo_soup.find('relative-time')
        last_updated = rel_time_tag['datetime'] if rel_time_tag else ""

        # Languages
        lang_spans = repo_soup.select('span[itemprop="programmingLanguage"]')
        alt_spans = repo_soup.select('span.color-fg-default.text-bold.mr-1')
        all_langs = [tag.text.strip() for tag in lang_spans + alt_spans if tag.text.strip()]
        languages = ', '.join(sorted(set(all_langs)))

        # Commits (via API)
        commits = get_commit_count(username, reponame)

        time.sleep(1)  # Be polite with GitHub
        return username, reponame, repo_url, stars, about, last_updated, languages, commits

    except Exception as e:
        print(f"Error scraping repository: {e}")
        return "", "", "", "", "", "", "", ""

def get_topic_page(topic_url):
    response = requests.get(topic_url, headers=get_headers())
    if response.status_code != 200:
        raise Exception(f'Failed to load page {topic_url}')
    return BeautifulSoup(response.text, 'html.parser')

def get_topic_repos(topic_doc):
    repo_tags = topic_doc.find_all('h3', {'class': 'f3 color-fg-muted text-normal lh-condensed'})
    stars_tags = topic_doc.find_all('span', {'class': 'Counter js-social-count'})

    topic_repo_dicts = {
        'Username': [], 'Repo_Name': [], 'Repo_Url': [], 'Stars': [],
        'About': [], 'Last_Updated': [], 'Languages': [], 'Commits': []
    }

    for i in range(len(repo_tags)):
        repo_info = get_repo_info(repo_tags[i], stars_tags[i])
        topic_repo_dicts['Username'].append(repo_info[0])
        topic_repo_dicts['Repo_Name'].append(repo_info[1])
        topic_repo_dicts['Repo_Url'].append(repo_info[2])
        topic_repo_dicts['Stars'].append(repo_info[3])
        topic_repo_dicts['About'].append(repo_info[4])
        topic_repo_dicts['Last_Updated'].append(repo_info[5])
        topic_repo_dicts['Languages'].append(repo_info[6])
        topic_repo_dicts['Commits'].append(repo_info[7])

    return pd.DataFrame(topic_repo_dicts)

def save_to_xml(df, filename):
    root = Element('Repositories')

    for _, row in df.iterrows():
        repo = SubElement(root, 'Repository')
        SubElement(repo, 'Username').text = str(row['Username'])
        SubElement(repo, 'Repo_Name').text = str(row['Repo_Name'])
        SubElement(repo, 'Repo_Url').text = str(row['Repo_Url'])
        SubElement(repo, 'Stars').text = str(row['Stars'])
        SubElement(repo, 'About').text = str(row['About'])
        SubElement(repo, 'Last_Updated').text = str(row['Last_Updated'])
        SubElement(repo, 'Languages').text = str(row['Languages'])
        SubElement(repo, 'Commits').text = str(row['Commits'])

    xml_str = minidom.parseString(tostring(root)).toprettyxml(indent="  ")
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(xml_str)

def scrape_topic(topic_url, topic_name):
    filename = f"{topic_name}_repos.xml"
    if os.path.exists(filename):
        print(f"File {filename} already exists. Skipping...")
        return

    print(f"Scraping {topic_name} repositories...")
    topic_df = get_topic_repos(get_topic_page(topic_url))
    save_to_xml(topic_df, filename)
    print(f"Saved {len(topic_df)} repositories to {filename}")

def scrape_arduino_and_bitcoin():
    topics = {
        "arduino": "https://github.com/topics/arduino",
        "bitcoin": "https://github.com/topics/bitcoin",
        "chrome" : "https://github.com/topics/chrome"
    }

    for name, url in topics.items():
        scrape_topic(url, name)
        print("\n" + "=" * 50 + "\n")

if __name__ == "__main__":
    scrape_arduino_and_bitcoin()