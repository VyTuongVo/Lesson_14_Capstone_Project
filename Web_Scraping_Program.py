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

def get_2000_plus_links(driver):
    driver.get("https://www.baseball-almanac.com/yearmenu.shtml")
    WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.TAG_NAME, "a"))
    )
    seasons = []
    for a in driver.find_elements(By.TAG_NAME, "a"):
        txt = a.text.strip()
        href = a.get_attribute("href") or ""
        if txt.isdigit():
            year = int(txt)
            if 2000 <= year <= 2025 and f"yr{txt}" in href:
                seasons.append((txt, href))
    print(f"▶ Will scrape {len(seasons)} seasons (2000–2025)")  # This will look at only season from 2000 to 2025
    # This is because the design of the page is different in the year. Hence I choosed 2000 - 2025 which have the same table design
    return seasons

def scrape_team_standings(driver, year, url):
    driver.get(url)
    roster_xpath = f"//tr[td/a[contains(@href,'roster.php?y={year}')]]"
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, roster_xpath))
        )
    except TimeoutException:
        print(f"⚠️ [{year}] no roster-row found, skipping")
        return []

    rows = driver.find_elements(By.XPATH, roster_xpath)
    records = []
    for tr in rows:
        tds = tr.find_elements(By.CSS_SELECTOR, "td.datacolBox")
        if len(tds) < 6:
            continue
        team    = tds[0].text.strip()  #Look at the 3rd table. We only look at the columsn!
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
        print(f"[{year}] has no valid rows")
    return records

def main():
    driver = setup_driver(headless=True)
    all_data = []
    try:
        seasons = get_2000_plus_links(driver)[:26]  # only first 26 seasons (2000–2025) --> I only want American League. If I do more it will take all league
        print(f"🔧 Testing on {len(seasons)} seasons")
        for year, link in seasons:
            print(f"→ Scraping {year}")
            recs = scrape_team_standings(driver, year, link)
            all_data.extend(recs)
    finally:
        driver.quit()

    if not all_data:
        print("No data collected.")
        return

    df = pd.DataFrame(all_data)
    df.to_csv("american_league_team_standings_2000_2025_sample.csv", index=False)
    print("Saved american_league_team_standings_2000_2025_sample.csv")

if __name__ == "__main__":
    main()
