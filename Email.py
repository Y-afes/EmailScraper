import requests
from bs4 import BeautifulSoup
import re
from tqdm import tqdm
from urllib.parse import quote
import signal
import sys
from validate_email_address import validate_email

continue_scanning = True


VALID_DOMAINS = {"com", "org", "net", "edu", "gov", "mil", "int"}
VALID_CC_TLDS = {"tr", "uk", "us", "de", "fr", "ru", "cn", "jp", "in"} 

def google_search(query):
    encoded_query = quote(query, safe='')
    url = f"https://www.google.com/search?q={encoded_query}&num=1000"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.text

def extract_emails_from_page(url):
    emails = set()
    try:
        response = requests.get(url)
        response.raise_for_status()

        content = response.content.decode('utf-8', errors='ignore')
        soup = BeautifulSoup(content, "html.parser")

        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

        for email in re.findall(email_pattern, content):
            if is_valid_email_format(email):
                emails.add(email.lower())

        for tag in soup.find_all(['p', 'div']):
            for email in re.findall(email_pattern, tag.get_text()):
                if is_valid_email_format(email):
                    emails.add(email.lower())

    except requests.exceptions.RequestException:
        pass

    return emails

def is_valid_email_format(email):
    if any(char in email for char in ['%', '#', '$', '&', '*', '|']):
        return False

    parts = email.split('.')
    domain = parts[-1].lower()
    second_level_domain = parts[-2].lower() if len(parts) > 2 else ''

    if domain not in VALID_DOMAINS and domain not in VALID_CC_TLDS and second_level_domain not in VALID_DOMAINS:
        return False

    return True

def validate_and_save_emails(emails):
    valid_emails = set()

    for email in emails:
        if validate_email(email):
            valid_emails.add(email)
            tqdm.write(f"Valid email: {email}")

    with open("emails.txt", "a", encoding="utf-8") as file:
        existing_emails = read_existing_emails()
        for email in valid_emails:
            if email not in existing_emails:
                file.write(email + ",\n")
                tqdm.write(f"Saved email: {email}")

    return valid_emails

def read_existing_emails():
    existing_emails = set()
    try:
        with open("emails.txt", "r", encoding="utf-8") as file:
            for line in file:
                email = line.strip().strip(',')
                if email:
                    existing_emails.add(email)
    except FileNotFoundError:
        pass

    return existing_emails

def signal_handler(sig, frame):
    global continue_scanning
    print("\nCtrl+C detected.\nYou can support me via crypto money.. \nBTC  ERC20  0x57f9f41ea14135bcbd7b0600762a34f6ae5e2878 \nUSDT ERC20  0x57f9f41ea14135bcbd7b0600762a34f6ae5e2878  \nETH  BEEP20 0x57f9f41ea14135bcbd7b0600762a34f6ae5e2878")
    continue_scanning = False
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    while continue_scanning:
        query = input("author>0_rhpositive\nGoogle E-mail Scraper: ")

        try:
            search_results = google_search(query)

            soup = BeautifulSoup(search_results, "html.parser")
            links = soup.find_all("a", href=True)
            urls = [link["href"] for link in links if link["href"].startswith("http")]

            emails_found = set()

            with tqdm(total=len(urls), desc="Progress", unit="page", leave=False) as pbar:
                for url in urls:
                    if not continue_scanning:
                        break
                    if "google.com" not in url:
                        emails = extract_emails_from_page(url)
                        emails_found.update(emails)

                        valid_emails = validate_and_save_emails(emails_found)

                    pbar.update(1)

            print(f"\nTotal {len(valid_emails)} new valid email addresses found and saved to emails.txt.\n" "\nYou can support me via crypto money.. \nBTC   ERC20   0x57f9f41ea14135bcbd7b0600762a34f6ae5e2878  \nUSDT  ERC20   0x57f9f41ea14135bcbd7b0600762a34f6ae5e2878  \nETH   BEEP20  0x57f9f41ea14135bcbd7b0600762a34f6ae5e2878")

        except requests.exceptions.RequestException:
            pass

if __name__ == "__main__":
    main()
