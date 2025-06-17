import streamlit as st
import pandas as pd
import altair as alt

@st.cache_data
def load_data():


    df = pd.read_csv("american_league_team_standings_2000_2025_sample.csv")

    #cleaning the df again! Taking out all extra stuff... Doesn't look at Payroll. Its too inconsistance

    #print(df)
    df["Year"] = pd.to_numeric(
        df["Year"].astype(str).str.replace(r"[^\d]", "", regex=True),
        errors="coerce"
    ).astype(int)
    for col in ["Wins", "Losses"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(r"[^\d]", "", regex=True),
            errors="coerce"
        ).fillna(0).astype(int)
    df["WP"] = pd.to_numeric(
        df["WP"].astype(str).str.replace(r"[^\d\.]", "", regex=True),
        errors="coerce"
    )
    df["GB"] = pd.to_numeric(
        df["GB"].astype(str)
               .str.replace("½", ".5")
               .str.replace(r"[^\d\.]", "", regex=True),
        errors="coerce"
    )
    return df


def main():
    st.title("MLB American League Team Standings Dashboard")
    df = load_data()

    st.sidebar.header("Filters")

    years = sorted(df["Year"].unique())
    year_range = st.sidebar.slider(
        "Year Range",
        min_value=years[0],
        max_value=years[-1],
        value=(years[0], years[-1])
    )
    df = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])]

    # team multi-select
    teams = sorted(df["Team"].unique())
    selected_teams = st.sidebar.multiselect(
        "Select Teams",
        options=teams,
        default=teams[:5]
    )
    df = df[df["Team"].isin(selected_teams)]

    # Visualization 1: Wins Over Time --> This will be a line graph will selected time and their win over time
    st.header("Wins Over Time")
    line_chart = alt.Chart(df).mark_line(point=True).encode(
        x=alt.X("Year:O", title="Year"),
        y=alt.Y("Wins:Q", title="Wins"),
        color="Team:N"
    )
    st.altair_chart(line_chart, use_container_width=True)

    # Visualization 2: Average Wins per Team --> This is a bar graph of avberage win of selected year
    st.header("Average Wins per Team")
    avg_wins = df.groupby("Team")["Wins"].mean().reset_index()
    bar_chart_wins = alt.Chart(avg_wins).mark_bar().encode(
        x=alt.X("Team:N", sort="-y", title="Team"),
        y=alt.Y("Wins:Q", title="Avg Wins"),
        tooltip=["Team", "Wins"]
    )
    st.altair_chart(bar_chart_wins, use_container_width=True)

    # Visualization 3: Losses per Team in Final Year --> This is again a bar graph of average lost of selected year
    st.header(f"Losses per Team in {year_range[1]}")
    df_final = df[df["Year"] == year_range[1]]
    if df_final.empty:
        st.warning(f"No data available for {year_range[1]}.")
    else:
        bar_chart_losses = alt.Chart(df_final).mark_bar().encode(
            x=alt.X("Team:N", sort="-y", title="Team"),
            y=alt.Y("Losses:Q", title="Losses"),
            color="Team:N",
            tooltip=["Team", "Losses"]
        )
        st.altair_chart(bar_chart_losses, use_container_width=True)

if __name__ == "__main__":
    main()
