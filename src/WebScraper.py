import re, time
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
from pylatexenc.latex2text import LatexNodes2Text
import pandas as pd
from typing import List, Dict
import json

def latex_to_text(latex: str) -> str:
    if not latex:
        return ""
    return LatexNodes2Text().latex_to_text(latex)

def clean_rendered_mathjax_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    for sub in soup.find_all("sub"):
        sub.replace_with("_" + sub.get_text())
    for sup in soup.find_all("sup"):
        sup.replace_with("^" + sup.get_text())

    for script in soup.find_all('script'):
        t = script.get('type', '')
        if t.startswith('math/tex') or 'math' in t:
            latex_source = script.string or ''
            replacement = latex_to_text(latex_source)
            script.replace_with(soup.new_string(replacement))

    html_text = str(soup)

    html_text = re.sub(r'\$\$\$(.*?)\$\$\$', lambda m: latex_to_text(m.group(1)), html_text)
    html_text = re.sub(r'\\(texttt|mathrm|underline|textsuperscript)\{(.*?)\}', r'\2', html_text)

    html_text = html_text.replace(r'\le', '≤').replace(r'\ge', '≥')
    html_text = html_text.replace(r'\cdot', '·').replace(r'\times', '×')
    html_text = html_text.replace(r'\to', '→').replace(r'\rightarrow', '→')
    html_text = html_text.replace(r'\ldots', '...').replace(r'\dots', '...')

    soup2 = BeautifulSoup(html_text, 'html.parser')
    text = soup2.get_text(separator=' ', strip=True)

    text = re.sub(r'\b([^\s]+)\s+\1\b', r'\1', text)
    text = ' '.join(text.split())

    return text


# main function
def fetch_and_clean_one(problem_id, delay=3):
    url = f"https://codeforces.com/contest/{problem_id.split('_')[0]}/problem/{problem_id.split('_')[1]}"
    
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-infobars",
            ]
        )
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/114.0.0.0 Safari/537.36"
        )
        try:
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            
            if not response or response.status != 200:
                print(f"Failed to fetch {url}, status: {response.status if response else 'No response'}")
                return None
            
            page.wait_for_selector("div.problem-statement", timeout=10000)
            html = page.inner_html("div.problem-statement")

            cleaned = clean_rendered_mathjax_html(html)
            return cleaned
        
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None

        finally:
            browser.close()
            time.sleep(delay)
