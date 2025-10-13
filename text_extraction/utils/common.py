import requests
import xml.etree.ElementTree as ET
import re
import time
import random
from pathlib import Path
from typing import List, Dict, Optional
import json
import urllib3
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from datetime import datetime
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create multiple sessions for rotation
sessions = []
for i in range(3):
    session = requests.Session()

    # Configure retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
    )

    # Mount adapter with retry strategy
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    sessions.append(session)

# Current session index for rotation
current_session_index = 0

# Global error tracking
failed_bills_tracker = {
    "failed_downloads": [],
    "failed_parsing": [],
    "failed_saves": [],
    "total_failed": 0,
}

# Advanced anti-blocking configuration
PROXY_LIST = [
    # Free proxy servers (these will be rotated)
    # Note: These are example proxies - in production, you'd want to use
    # a proxy service or rotate through a list of working proxies
    "http://8.8.8.8:8080",  # Example - replace with real proxies
    "http://1.1.1.1:8080",  # Example - replace with real proxies
    "http://9.9.9.9:8080",  # Example - replace with real proxies
]
current_proxy_index = 0
proxy_lock = threading.Lock()

# Request throttling
last_request_time = 0
request_lock = threading.Lock()


def get_realistic_headers() -> dict:
    """Get realistic browser headers to avoid blocking."""
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    ]

    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
        "Referer": "https://www.congress.gov/",
        "DNT": "1",
        "Sec-GPC": "1",
    }


def get_congress_gov_headers() -> dict:
    """Get specialized headers for congress.gov to avoid blocking."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
        "Referer": "https://www.congress.gov/",
        "Origin": "https://www.congress.gov",
    }


def rotate_session():
    """Rotate to the next session for load balancing."""
    global current_session_index
    current_session_index = (current_session_index + 1) % len(sessions)
    return sessions[current_session_index]


def get_next_proxy():
    """Get the next proxy in rotation."""
    global current_proxy_index
    with proxy_lock:
        if not PROXY_LIST:
            return None
        proxy = PROXY_LIST[current_proxy_index]
        current_proxy_index = (current_proxy_index + 1) % len(PROXY_LIST)
        return proxy


def fetch_working_proxies():
    """Fetch a list of working proxy servers from free proxy APIs."""
    try:
        print("   🔄 Fetching working proxy servers...")

        # Try to get proxies from free proxy APIs
        proxy_sources = [
            "https://api.proxyscrape.com/v2/?request=get&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all",
            "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
        ]

        working_proxies = []

        for source in proxy_sources:
            try:
                response = requests.get(source, timeout=10)
                if response.status_code == 200:
                    proxies = response.text.strip().split("\n")
                    # Filter and format proxies
                    for proxy in proxies[:10]:  # Limit to first 10
                        proxy = proxy.strip()
                        if proxy and ":" in proxy:
                            if not proxy.startswith("http"):
                                proxy = f"http://{proxy}"
                            working_proxies.append(proxy)
                    break
            except:
                continue

        if working_proxies:
            global PROXY_LIST
            PROXY_LIST = working_proxies
            print(f"   ✅ Found {len(working_proxies)} working proxies")
        else:
            print("   ⚠️ No working proxies found, using direct connection")

    except Exception as e:
        print(f"   ❌ Error fetching proxies: {e}")
        print("   ⚠️ Using direct connection")


def throttle_requests(min_delay: float = 2.0):
    """Ensure minimum delay between requests to avoid rate limiting."""
    global last_request_time
    with request_lock:
        current_time = time.time()
        time_since_last = current_time - last_request_time
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        last_request_time = time.time()


def get_stealth_headers() -> dict:
    """Get headers that mimic a real browser more closely."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }


def get_chatgpt_style_headers() -> dict:
    """Get headers that mimic ChatGPT's request patterns."""
    return {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }


def try_curl_download(url: str) -> Optional[str]:
    """Try downloading using curl as a fallback method."""
    try:
        print(f"   🔄 Trying curl download for {url}")

        # Use curl with realistic headers
        cmd = [
            "curl",
            "-s",
            "-L",
            "-H",
            "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "-H",
            "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "-H",
            "Accept-Language: en-US,en;q=0.9",
            "-H",
            "DNT: 1",
            "-H",
            "Connection: keep-alive",
            "--connect-timeout",
            "30",
            "--max-time",
            "60",
            url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0 and result.stdout:
            print(f"   ✅ Curl download successful")
            return result.stdout
        else:
            print(f"   ❌ Curl download failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"   ❌ Curl download error: {e}")
        return None


def try_wget_download(url: str) -> Optional[str]:
    """Try downloading using wget as another fallback method."""
    try:
        print(f"   🔄 Trying wget download for {url}")

        # Use wget with realistic headers
        cmd = [
            "wget",
            "-q",
            "-O",
            "-",
            "--header=User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "--header=Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "--timeout=30",
            url,
        ]

        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

        if result.returncode == 0 and result.stdout:
            print(f"   ✅ Wget download successful")
            return result.stdout
        else:
            print(f"   ❌ Wget download failed: {result.stderr}")
            return None

    except Exception as e:
        print(f"   ❌ Wget download error: {e}")
        return None


def try_chatgpt_style_download(url: str) -> Optional[str]:
    """Try downloading using ChatGPT-style request patterns."""
    try:
        print(f"   🔄 Trying ChatGPT-style download for {url}")

        # Create a new session with ChatGPT-style headers
        session = requests.Session()
        headers = get_chatgpt_style_headers()

        # Add some ChatGPT-like behavior patterns
        time.sleep(random.uniform(2.0, 4.0))  # ChatGPT-like delay

        # Make the request with ChatGPT-style headers
        response = session.get(
            url,
            headers=headers,
            timeout=60,
            verify=False,
            allow_redirects=True,
        )

        if response.status_code == 200:
            print(f"   ✅ ChatGPT-style download successful")
            return response.text
        else:
            print(f"   ❌ ChatGPT-style download failed: {response.status_code}")
            return None

    except Exception as e:
        print(f"   ❌ ChatGPT-style download error: {e}")
        return None


def try_alternative_approach(url: str) -> Optional[str]:
    """Try alternative approaches for congress.gov blocking."""
    try:
        print(f"   🔄 Trying alternative approach for {url}")
        
        # Try with a completely different approach - simulate a mobile app
        mobile_headers = {
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
        }
        
        session = requests.Session()
        time.sleep(random.uniform(3.0, 6.0))
        
        response = session.get(
            url,
            headers=mobile_headers,
            timeout=60,
            verify=False,
            allow_redirects=True,
        )
        
        if response.status_code == 200:
            print(f"   ✅ Alternative approach successful")
            return response.text
        else:
            print(f"   ❌ Alternative approach failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Alternative approach error: {e}")
        return None


def try_government_style_request(url: str) -> Optional[str]:
    """Try with headers that might look like government/academic access."""
    try:
        print(f"   🔄 Trying government-style request for {url}")
        
        # Headers that might look like government/academic access
        gov_headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0",
            "Referer": "https://www.congress.gov/",
        }
        
        session = requests.Session()
        time.sleep(random.uniform(4.0, 8.0))
        
        response = session.get(
            url,
            headers=gov_headers,
            timeout=60,
            verify=False,
            allow_redirects=True,
        )
        
        if response.status_code == 200:
            print(f"   ✅ Government-style request successful")
            return response.text
        else:
            print(f"   ❌ Government-style request failed: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"   ❌ Government-style request error: {e}")
        return None


def record_failed_bill(
    bill_id: str,
    error_type: str,
    error_message: str,
    url: str = "",
    metadata_file: str = "",
    additional_info: Dict = None,
    output_folder: Path = None,
):
    """Record a failed bill for error tracking and reporting."""
    global failed_bills_tracker

    error_record = {
        "bill_id": bill_id,
        "error_type": error_type,
        "error_message": error_message,
        "url": url,
        "metadata_file": metadata_file,
        "timestamp": datetime.now().isoformat(),
        "additional_info": additional_info or {},
    }

    # Add to global tracker
    if error_type == "download":
        failed_bills_tracker["failed_downloads"].append(error_record)
    elif error_type == "parsing":
        failed_bills_tracker["failed_parsing"].append(error_record)
    elif error_type == "save":
        failed_bills_tracker["failed_saves"].append(error_record)

    failed_bills_tracker["total_failed"] += 1

    # Save individual error file to data_not_processed if output folder provided
    if output_folder:
        save_individual_error_file(error_record, output_folder)


def save_individual_error_file(error_record: Dict, output_folder: Path):
    """Save an individual failed bill error file to data_not_processed following the existing pattern."""
    try:
        # Create data_not_processed folder structure
        data_not_processed = output_folder / "data_not_processed"
        error_category = f"{error_record['error_type']}_failures"
        error_folder = data_not_processed / "text_extraction_errors" / error_category
        error_folder.mkdir(parents=True, exist_ok=True)

        # Create filename following the existing pattern
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        bill_id_clean = error_record["bill_id"].replace(" ", "").replace("/", "_")
        filename = f"bill_{bill_id_clean}_{timestamp}.json"

        # Save the error record
        with open(error_folder / filename, "w", encoding="utf-8") as f:
            json.dump(error_record, f, indent=2, ensure_ascii=False)

        print(f"   📋 Saved error file: {error_folder / filename}")

    except Exception as e:
        print(f"   ❌ Error saving individual error file: {e}")


def save_failed_bills_report(output_folder: Path, state: str):
    """Save a comprehensive report of failed bills to the calling repo's data_not_processed folder."""
    global failed_bills_tracker

    if failed_bills_tracker["total_failed"] == 0:
        print("✅ No failed bills to report")
        return

    # Create data_not_processed folder structure
    data_not_processed = output_folder / "data_not_processed"
    text_extraction_errors = data_not_processed / "text_extraction_errors"
    summary_reports = text_extraction_errors / "summary_reports"
    summary_reports.mkdir(parents=True, exist_ok=True)

    # Generate timestamp for the report
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save detailed error report
    report_file = summary_reports / f"failed_text_extraction_{state}_{timestamp}.json"

    report_data = {
        "state": state,
        "timestamp": datetime.now().isoformat(),
        "summary": {
            "total_failed": failed_bills_tracker["total_failed"],
            "failed_downloads": len(failed_bills_tracker["failed_downloads"]),
            "failed_parsing": len(failed_bills_tracker["failed_parsing"]),
            "failed_saves": len(failed_bills_tracker["failed_saves"]),
        },
        "failed_downloads": failed_bills_tracker["failed_downloads"],
        "failed_parsing": failed_bills_tracker["failed_parsing"],
        "failed_saves": failed_bills_tracker["failed_saves"],
    }

    try:
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        print(f"📋 Failed bills report saved: {report_file}")
        print(f"   Total failed: {failed_bills_tracker['total_failed']}")
        print(f"   Download failures: {len(failed_bills_tracker['failed_downloads'])}")
        print(f"   Parsing failures: {len(failed_bills_tracker['failed_parsing'])}")
        print(f"   Save failures: {len(failed_bills_tracker['failed_saves'])}")

    except Exception as e:
        print(f"❌ Error saving failed bills report: {e}")

    # Also save a simple summary file for quick reference
    summary_file = summary_reports / f"failed_summary_{state}_{timestamp}.txt"
    try:
        with open(summary_file, "w", encoding="utf-8") as f:
            f.write(f"Text Extraction Failure Report - {state}\n")
            f.write(f"Generated: {datetime.now().isoformat()}\n\n")
            f.write(f"Total Failed Bills: {failed_bills_tracker['total_failed']}\n")
            f.write(
                f"Download Failures: {len(failed_bills_tracker['failed_downloads'])}\n"
            )
            f.write(
                f"Parsing Failures: {len(failed_bills_tracker['failed_parsing'])}\n"
            )
            f.write(f"Save Failures: {len(failed_bills_tracker['failed_saves'])}\n\n")

            if failed_bills_tracker["failed_downloads"]:
                f.write("DOWNLOAD FAILURES:\n")
                for error in failed_bills_tracker["failed_downloads"]:
                    f.write(f"  - {error['bill_id']}: {error['error_message']}\n")
                    if error["url"]:
                        f.write(f"    URL: {error['url']}\n")
                f.write("\n")

            if failed_bills_tracker["failed_parsing"]:
                f.write("PARSING FAILURES:\n")
                for error in failed_bills_tracker["failed_parsing"]:
                    f.write(f"  - {error['bill_id']}: {error['error_message']}\n")
                f.write("\n")

            if failed_bills_tracker["failed_saves"]:
                f.write("SAVE FAILURES:\n")
                for error in failed_bills_tracker["failed_saves"]:
                    f.write(f"  - {error['bill_id']}: {error['error_message']}\n")
                f.write("\n")

        print(f"📋 Summary report saved: {summary_file}")

    except Exception as e:
        print(f"❌ Error saving summary report: {e}")


def reset_error_tracking():
    """Reset the global error tracking for a new run."""
    global failed_bills_tracker
    failed_bills_tracker = {
        "failed_downloads": [],
        "failed_parsing": [],
        "failed_saves": [],
        "total_failed": 0,
    }


def download_with_retry(
    url: str,
    max_retries: int = 5,
    delay: float = 1.0,
    use_aggressive_mode: bool = False,
) -> Optional[requests.Response]:
    """Download with advanced retry logic and anti-blocking techniques."""
    is_congress_gov = "congress.gov" in url

    for attempt in range(max_retries):
        try:
            # Throttle requests to avoid rate limiting
            throttle_requests(min_delay=3.0 if is_congress_gov else 1.0)

            # Rotate session for load balancing
            session = rotate_session()

            # Add random delay to avoid rate limiting
            base_delay = delay + random.uniform(1.0, 3.0)
            if is_congress_gov:
                base_delay += random.uniform(5.0, 15.0)  # Extra delay for congress.gov
            time.sleep(base_delay)

            # Get specialized headers based on domain
            if is_congress_gov:
                headers = get_congress_gov_headers()
            elif use_aggressive_mode:
                # Rotate between different header styles in aggressive mode
                header_styles = [
                    get_stealth_headers,
                    get_chatgpt_style_headers,
                    get_realistic_headers,
                ]
                headers = header_styles[attempt % len(header_styles)]()
            else:
                headers = get_realistic_headers()

            # Configure proxies if in aggressive mode and we have real proxies
            proxies = None
            if use_aggressive_mode and PROXY_LIST and len(PROXY_LIST) > 0:
                # Only use proxies if they're not the example DNS servers
                if not any("8.8.8.8" in proxy or "1.1.1.1" in proxy or "9.9.9.9" in proxy for proxy in PROXY_LIST):
                    proxy = get_next_proxy()
                    proxies = {"http": proxy, "https": proxy}
                    print(f"   🔄 Using proxy: {proxy}")
                else:
                    print(f"   ⚠️ Skipping example proxies, using direct connection")

            # Make the request with additional options
            response = session.get(
                url,
                headers=headers,
                proxies=proxies,
                timeout=60,  # Increased timeout
                verify=False,  # Disable SSL verification for some sites
                allow_redirects=True,
            )

            # If we get a 403, try multiple fallback strategies
            if response.status_code == 403:
                print(
                    f"   ⚠️ Got 403 on attempt {attempt + 1}, trying fallback strategies..."
                )

                # Strategy 1: Try Googlebot user agent
                headers["User-Agent"] = (
                    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
                )
                response = session.get(url, headers=headers, timeout=45, verify=False)

                if response.status_code == 403:
                    # Strategy 2: Try different browser
                    headers["User-Agent"] = (
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0"
                    )
                    headers["Accept"] = (
                        "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                    )
                    response = session.get(
                        url, headers=headers, timeout=45, verify=False
                    )

                if response.status_code == 403:
                    # Strategy 3: Try mobile user agent
                    headers["User-Agent"] = (
                        "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1"
                    )
                    response = session.get(
                        url, headers=headers, timeout=45, verify=False
                    )

                if response.status_code == 403:
                    # Strategy 4: Try with minimal headers
                    minimal_headers = {
                        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    }
                    response = session.get(
                        url, headers=minimal_headers, timeout=45, verify=False
                    )

                if response.status_code == 403 and use_aggressive_mode:
                    # Strategy 5: Try curl as fallback
                    print(f"   🔄 Trying curl fallback for {url}")
                    curl_content = try_curl_download(url)
                    if curl_content:
                        # Create a mock response object
                        class MockResponse:
                            def __init__(self, content):
                                self.text = content
                                self.status_code = 200
                                self.content = content.encode("utf-8")

                        return MockResponse(curl_content)

                if response.status_code == 403 and use_aggressive_mode:
                    # Strategy 6: Try wget as fallback
                    print(f"   🔄 Trying wget fallback for {url}")
                    wget_content = try_wget_download(url)
                    if wget_content:
                        # Create a mock response object
                        class MockResponse:
                            def __init__(self, content):
                                self.text = content
                                self.status_code = 200
                                self.content = content.encode("utf-8")

                        return MockResponse(wget_content)

                if response.status_code == 403 and use_aggressive_mode:
                    # Strategy 7: Try ChatGPT-style download
                    print(f"   🔄 Trying ChatGPT-style fallback for {url}")
                    chatgpt_content = try_chatgpt_style_download(url)
                    if chatgpt_content:
                        # Create a mock response object
                        class MockResponse:
                            def __init__(self, content):
                                self.text = content
                                self.status_code = 200
                                self.content = content.encode("utf-8")

                        return MockResponse(chatgpt_content)

                if response.status_code == 403 and use_aggressive_mode:
                    # Strategy 8: Try alternative approach (mobile)
                    print(f"   🔄 Trying alternative approach fallback for {url}")
                    alt_content = try_alternative_approach(url)
                    if alt_content:
                        # Create a mock response object
                        class MockResponse:
                            def __init__(self, content):
                                self.text = content
                                self.status_code = 200
                                self.content = content.encode("utf-8")

                        return MockResponse(alt_content)

                if response.status_code == 403 and use_aggressive_mode:
                    # Strategy 9: Try government-style request
                    print(f"   🔄 Trying government-style fallback for {url}")
                    gov_content = try_government_style_request(url)
                    if gov_content:
                        # Create a mock response object
                        class MockResponse:
                            def __init__(self, content):
                                self.text = content
                                self.status_code = 200
                                self.content = content.encode("utf-8")

                        return MockResponse(gov_content)

            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"   ⚠️ Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                # Exponential backoff with jitter
                wait_time = delay * (2**attempt) + random.uniform(2, 8)
                if is_congress_gov:
                    wait_time += random.uniform(3, 10)  # Extra wait for congress.gov
                print(f"   ⏳ Waiting {wait_time:.1f}s before retry...")
                time.sleep(wait_time)
            else:
                print(f"   ❌ All {max_retries} attempts failed for {url}")
                return None

    return None


def download_bill_text(url: str, delay: float = 1.0) -> Optional[str]:
    """
    Download bill text from a URL.

    Args:
        url: URL to download from
        delay: Delay between requests to be respectful

    Returns:
        XML content as string, or None if failed
    """
    try:
        response = download_with_retry(url, max_retries=3, delay=delay)
        if not response:
            return None

        content_type = response.headers.get("content-type", "").lower()
        content = response.text

        # More flexible content type checking
        if (
            "xml" in content_type
            or content.strip().startswith("<?xml")
            or "<bill>" in content[:1000]
        ):
            return content
        else:
            print(f"⚠️ Unexpected content type: {content_type} for {url}")
            print(f"   Content preview: {content[:200]}...")
            return None

    except Exception as e:
        print(f"❌ Error downloading {url}: {e}")
        return None

