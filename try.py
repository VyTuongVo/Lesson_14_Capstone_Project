import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

def setup_driver(headless=True):
    opts = Options()
    if headless:
        opts.add_argument("--headless")
    opts.add_argument("user-agent=Mozilla/5.0")
    driver = webdriver.Chrome(options=opts)
    driver.set_page_load_timeout(30)
    return driver

def get_seasons(driver):
    driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
    )
    seasons = []
    for a in driver.find_elements(By.TAG_NAME, "a"):
        txt = a.text.strip()
        href = a.get_attribute("href") or ""
        if txt.isdigit():
            y = int(txt)
            if 2000 <= y <= 2025 and f"yr{txt}" in href:
                seasons.append((txt, href))
    print(f"▶ Found {len(seasons)} seasons (2000–2025)")
    return seasons

def scrape_standings(driver, year, url):
    try:
        driver.get(url)
    except WebDriverException as e:
        print(f"⚠️ [{year}] load error: {e}")
        return []

    # wait for ba-table sections
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div.ba-table"))
    )

    # pick the ba-table that contains a roster link for this year
    target_div = None
    for ba in driver.find_elements(By.CSS_SELECTOR, "div.ba-table"):
        if ba.find_elements(By.CSS_SELECTOR, f"a[href*='roster.php?y={year}']"):
            target_div = ba
            break

    if not target_div:
        print(f"⚠️ [{year}] no ba-table with roster links")
        return []

    # grab the boxed table and skip its first two header rows
    try:
        table = target_div.find_element(By.CSS_SELECTOR, "table.boxed")
    except:
        print(f"⚠️ [{year}] boxed table not found")
        return []

    rows = table.find_elements(By.CSS_SELECTOR, "tbody > tr")[2:]
    records = []
    for tr in rows:
        tds = tr.find_elements(By.CSS_SELECTOR, "td.datacolBox")
        if len(tds) != 6:
            continue
        team    = tds[0].text.strip()
        wins    = tds[1].text.strip()
        losses  = tds[2].text.strip()
        wp      = tds[3].text.strip()
        gb      = tds[4].text.strip()
        payroll = tds[5].text.strip()
        records.append({
            "Year":    year,
            "Team":    team,
            "Wins":    wins,
            "Losses":  losses,
            "WP":      wp,
            "GB":      gb,
            "Payroll": payroll
        })

    if not records:
        print(f"⚠️ [{year}] no valid rows")
    return records

def main():
    driver = setup_driver(headless=True)
    all_data = []
    try:
        seasons = get_seasons(driver)[:26]  # ← only the first 25 seasons (2000–2024)
        print(f"🔧 Testing on {len(seasons)} seasons")
        for year, link in seasons:
            print(f"→ Scraping {year}")
            recs = scrape_standings(driver, year, link)
            all_data.extend(recs)
    finally:
        driver.quit()

    if not all_data:
        print("❌ No data collected.")
        return

    df = pd.DataFrame(all_data)
    df.to_csv("american_league_team_standings_2000_2024_sample.csv", index=False)
    print("✅ Saved american_league_team_standings_2000_2024_sample.csv")

if __name__ == "__main__":
    main()
