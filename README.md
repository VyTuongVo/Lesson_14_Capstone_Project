In this project, I’ll leverage my data-scraping, data-analysis, query-writing, and coding skills to extract and examine the Year-by-Year MLB History site (https://www.baseball-almanac.com/yearmenu.shtml). Although the site archives National League data back to 1876, I’m focusing exclusively on the American League. I initially planned to harvest every season from 1901 through the present, but variations in table structure across decades proved challenging. To keep things manageable, I narrowed the scope to the “American League – Team Standings” table for 2000–2025. This table is clear, consistent, and—despite my limited baseball background—easy for me to interpret and explain.

The repository is organized into four main Python programs, which should be run in the order listed:
- Web_Scraping_Program.py: Connects to each selected year’s page, scrapes the “American League – Team Standings” table, and writes the results to american_league_team_standings_2000_2025_sample.csv.
- Database_Import_Program.py: Cleans and normalizes the CSV data, then imports it into an SQLite database named mlb_history.db.
- Database_Query_Program.py: Provides a simple CLI for users to run queries, perform joins, and edit or enrich the data as needed.
- Dashboard_Program.py: Uses Streamlit to build three interactive visualizations - 1. Wins over time (2000–2025) 2. Average wins per team for a selected year 3. Average losses per team for a selected year
  
By following this pipeline, I can go from raw HTML tables to an interactive dashboard that highlights trends in American League team performance.
