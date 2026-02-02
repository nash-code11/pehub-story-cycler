#!/usr/bin/env python3
"""
Story Cycler - Automatically cycles through top stories on a website.
Opens a browser window and navigates through stories one by one.
"""

import time
import argparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager


def setup_driver(fullscreen=False):
    """Set up Chrome driver with appropriate options."""
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--disable-popup-blocking")

    if fullscreen:
        chrome_options.add_argument("--kiosk")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver


def find_story_links(driver, base_url):
    """Find top story links on the page."""
    stories = []

    # Wait for page to load
    time.sleep(3)

    # Common selectors for story links on news sites
    selectors = [
        # PEHub specific selectors
        "article a",
        ".post-title a",
        ".entry-title a",
        "h2 a",
        "h3 a",
        # Generic news site selectors
        ".story-link",
        ".headline a",
        ".article-link",
        "[data-testid='story-link']",
        ".card a",
        ".news-item a",
    ]

    seen_urls = set()

    for selector in selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for elem in elements:
                href = elem.get_attribute("href")
                text = elem.text.strip()

                # Filter for actual article links
                if href and text and len(text) > 10:
                    # Make sure it's a story URL (not navigation, social, etc.)
                    if (base_url in href and
                        href not in seen_urls and
                        not any(skip in href.lower() for skip in [
                            '/tag/', '/category/', '/author/', '/page/',
                            'twitter.com', 'facebook.com', 'linkedin.com',
                            '#', 'javascript:', 'mailto:'
                        ])):
                        seen_urls.add(href)
                        stories.append({
                            'url': href,
                            'title': text[:100]  # Truncate long titles
                        })

                        # Limit to top stories
                        if len(stories) >= 15:
                            break

            if len(stories) >= 15:
                break

        except Exception as e:
            continue

    return stories


def display_story_info(driver, story, index, total):
    """Display an overlay with story information."""
    # Inject CSS and overlay
    overlay_script = f"""
    // Remove existing overlay if present
    var existingOverlay = document.getElementById('story-cycler-overlay');
    if (existingOverlay) existingOverlay.remove();

    // Create overlay
    var overlay = document.createElement('div');
    overlay.id = 'story-cycler-overlay';
    overlay.innerHTML = `
        <div style="
            position: fixed;
            bottom: 20px;
            left: 20px;
            right: 20px;
            background: rgba(0, 0, 0, 0.85);
            color: white;
            padding: 15px 20px;
            border-radius: 10px;
            z-index: 999999;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <div style="font-size: 12px; color: #aaa; margin-bottom: 5px;">
                        Story {index + 1} of {total}
                    </div>
                    <div style="font-size: 16px; font-weight: 500;">
                        {story['title'][:80]}{'...' if len(story['title']) > 80 else ''}
                    </div>
                </div>
                <div style="
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    border: 3px solid #4CAF50;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 18px;
                    font-weight: bold;
                    margin-left: 20px;
                " id="countdown-timer">
                </div>
            </div>
            <div style="
                margin-top: 10px;
                height: 4px;
                background: rgba(255,255,255,0.2);
                border-radius: 2px;
                overflow: hidden;
            ">
                <div id="progress-bar" style="
                    height: 100%;
                    background: #4CAF50;
                    width: 0%;
                    transition: width 1s linear;
                "></div>
            </div>
        </div>
    `;
    document.body.appendChild(overlay);
    """
    driver.execute_script(overlay_script)


def update_countdown(driver, seconds_remaining, total_seconds):
    """Update the countdown timer and progress bar."""
    progress = ((total_seconds - seconds_remaining) / total_seconds) * 100
    script = f"""
    var timer = document.getElementById('countdown-timer');
    var progress = document.getElementById('progress-bar');
    if (timer) timer.textContent = '{seconds_remaining}';
    if (progress) progress.style.width = '{progress}%';
    """
    try:
        driver.execute_script(script)
    except:
        pass


def cycle_stories(url, display_time=15, loop=True, fullscreen=False):
    """Main function to cycle through stories."""
    print(f"\n🚀 Starting Story Cycler")
    print(f"   URL: {url}")
    print(f"   Display time: {display_time} seconds per story")
    print(f"   Loop: {'Yes' if loop else 'No'}")
    print(f"\n   Press Ctrl+C to stop\n")

    driver = setup_driver(fullscreen)

    try:
        # Navigate to the main page
        print("📄 Loading homepage...")
        driver.get(url)

        # Wait for page to fully load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        time.sleep(3)  # Additional wait for dynamic content

        # Extract base URL for filtering
        from urllib.parse import urlparse
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"

        # Find stories
        print("🔍 Finding top stories...")
        stories = find_story_links(driver, base_url)

        if not stories:
            print("❌ No stories found. The site structure may need custom selectors.")
            print("   Keeping browser open for manual inspection...")
            input("   Press Enter to close...")
            return

        print(f"✅ Found {len(stories)} stories to cycle through:\n")
        for i, story in enumerate(stories, 1):
            print(f"   {i}. {story['title'][:60]}...")
        print()

        # Cycle through stories
        cycle_count = 0
        while True:
            cycle_count += 1
            print(f"\n{'='*50}")
            print(f"📺 Starting cycle #{cycle_count}")
            print(f"{'='*50}\n")

            for i, story in enumerate(stories):
                print(f"📖 [{i+1}/{len(stories)}] {story['title'][:50]}...")

                # Navigate to story
                driver.get(story['url'])

                # Wait for page load
                try:
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                except TimeoutException:
                    print("   ⚠️  Page load timeout, continuing anyway...")

                time.sleep(1)  # Let page render

                # Display overlay
                display_story_info(driver, story, i, len(stories))

                # Get article end position for smooth scrolling
                # Try to find the end of the article content, not the full page
                scroll_target = driver.execute_script("""
                    // Common article container selectors
                    var selectors = [
                        'article',
                        '.article-content',
                        '.post-content',
                        '.entry-content',
                        '.story-content',
                        '.article-body',
                        '.post-body',
                        '[itemprop="articleBody"]',
                        '.content-body',
                        'main article',
                        '.single-post-content'
                    ];

                    for (var i = 0; i < selectors.length; i++) {
                        var el = document.querySelector(selectors[i]);
                        if (el) {
                            var rect = el.getBoundingClientRect();
                            var scrollTop = window.pageYOffset || document.documentElement.scrollTop;
                            // Return the bottom of the article element
                            return rect.bottom + scrollTop;
                        }
                    }

                    // Fallback: use 70% of page height (skip footer area)
                    return document.body.scrollHeight * 0.7;
                """)

                viewport_height = driver.execute_script("return window.innerHeight")
                scroll_distance = max(0, scroll_target - viewport_height)

                # Countdown with progress updates and smooth scrolling
                for remaining in range(display_time, 0, -1):
                    update_countdown(driver, remaining, display_time)

                    # Calculate scroll position based on time elapsed
                    time_elapsed = display_time - remaining
                    if scroll_distance > 0 and display_time > 1:
                        # Scroll progressively through the article
                        scroll_position = int((time_elapsed / (display_time - 1)) * scroll_distance)
                        driver.execute_script(f"window.scrollTo({{top: {scroll_position}, behavior: 'smooth'}})")

                    time.sleep(1)

                print(f"   ✓ Done")

            if not loop:
                print("\n🏁 Cycle complete!")
                break

            print(f"\n🔄 Restarting cycle...")
            # Go back to homepage to refresh stories
            driver.get(url)
            time.sleep(3)

    except KeyboardInterrupt:
        print("\n\n⏹️  Stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
    finally:
        print("🔒 Closing browser...")
        driver.quit()


def main():
    parser = argparse.ArgumentParser(
        description="Automatically cycle through top stories on a website"
    )
    parser.add_argument(
        "url",
        nargs="?",
        default="https://www.pehub.com/",
        help="Website URL to cycle through (default: https://www.pehub.com/)"
    )
    parser.add_argument(
        "-t", "--time",
        type=int,
        default=45,
        help="Seconds to display each story (default: 45)"
    )
    parser.add_argument(
        "--no-loop",
        action="store_true",
        help="Don't loop - stop after one cycle through all stories"
    )
    parser.add_argument(
        "-f", "--fullscreen",
        action="store_true",
        help="Run in fullscreen/kiosk mode"
    )

    args = parser.parse_args()

    cycle_stories(
        url=args.url,
        display_time=args.time,
        loop=not args.no_loop,
        fullscreen=args.fullscreen
    )


if __name__ == "__main__":
    main()
