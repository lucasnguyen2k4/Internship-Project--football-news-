import pandas as pd

CLUB_ALIASES = {
    "AFC Ajax": ["Ajax"],
    "Feyenoord Rotterdam": ["Feyenoord"],
    "PSV Eindhoven": ["PSV"],
    "Getafe CF": ["Getafe"],
    "RC Celta de Vigo": ["Celta Vigo"],
    "Deportivo Alavés": ["Alavés", "Alaves"],
    "Girona FC": ["Girona"],
    "UD Las Palmas": ["Las Palmas"],
    "Sevilla FC": ["Sevilla"],
    "CA Osasuna": ["Osasuna"],
    "CD Leganés": ["Leganés", "Leganes"],
    "Valencia CF": ["Valencia"],
    "Real Sociedad de Fútbol": ["Sociedad", "Real Sociedad"],
    "Rayo Vallecano de Madrid": ["Rayo Vallecano"],
    "RCD Mallorca": ["Mallorca"],
    "RCD Espanyol de Barcelona": ["Espanyol"],
    "Villareal CF": ["Villareal"],
    "Club Atlético de Madrid": ["Atletico Madrid", "Atlético de Madrid"],
    "Real Madrid CF": ["Real Madrid"],
    "Athletic Club": ["Athletic Bilbao"],
    "FC Barcelona": ["Barcelona", "Barca"],
    "Real Valladolid CF": ["Valladolid"],
    "Real Betis Balompié": ["Real Betis", "Betis"],
    "SC Braga": ["Braga"],
    "Sporting CP": ["Sporting Lisbon", "Sporting"],
    "FC Porto": ["Porto"],
    "SL Benfica": ["Benfica"],
    "Rangers FC": ["Rangers"],
    "Celtic FC": ["Celtic"],
    "Heart of Midlothian": ["Hearts"],
    "Aberdeen FC": ["Aberdeen"],
    "Olympique Marseille": ["Marseille"],
    "Olympique Lyonnais": ["Lyon"],
    "Paris Saint-Germain FC": ["PSG", "Paris St-Germain"],
    "Manchester United FC": ["Man United", "Man Utd", "Manchester United"],
    "Manchester City FC": ["Man City", "Manchester City"],
    "Tottenham Hotspur FC": ["Spurs", "Tottenham"],
    "Liverpool FC": ["Liverpool"],
    "Chelsea FC": ["Chelsea"],
    "Arsenal FC": ["Arsenal"],
    "Newcastle United FC": ["Newcastle"],
    "Aston Villa FC": ["Aston Villa", "Villa"],
    "Fulham FC": ["Fulham"],
    "Ipswich Town FC": ["Ipswich"],
    "Everton FC": ["Everton"],
    "Wolverhampton Wanderers FC": ["Wolves", "Wolverhampton"],
    "Brighton & Hove Albion FC": ["Brighton"],
    "Southampton FC": ["Southampton", "The Saints"],
    "Nottingham Forest FC": ["Nottingham Forest", "Forest"],
    "AFC Bournemouth": ["Bournemouth"],
    "West Ham United FC": ["West Ham United", "West Ham", "The Hammers"],
    "Brentford FC": ["Brentford"],
    "Crystal Palace FC": ["Crystal Palace"],
    "Leicester City FC": ["Leicester"],
    "Burnley FC": ["Burnley"],
    "Leeds United FC": ["Leeds"],
    "Coventry City FC": ["Coventry"],
    "Cardiff City FC": ["Cardiff"],
    "Sunderland AFC": ["Sunderland"],
    "Millwall FC": ["Millwall"],
    "Bristol City FC": ["Bristol City"],
    "AS Roma": ["Roma"],
    "FC Internazionale Milano": ["Inter Milan", "Inter"],
    "AC Milan": ["AC Milan"],
    "SSC Napoli": ["Napoli"],
    "Juventus FC": ["Juventus"],
    "Bologna FC 1909": ["Bologna"],
    "FC Bayern München": ["Bayern", "Bayern Munich"],
    "Borussia Dortmund": ["Dortmund"],
    "Bayer 04 Leverkusen": ["Leverkusen"]
}

def build_keyword_maps(domestic_csv="clubs_with_leagues.csv", euro_csv="european_clubs_in_leagues.csv"):
    df = pd.read_csv(domestic_csv)
    df_euro = pd.read_csv(euro_csv)

    KEYWORD_TO_CLUB = {}
    CLUB_TO_LEAGUE = {}
    CLUB_TO_EURO_COMPS = {}

    for _, row in df.iterrows():
        club = row["club_name"].strip()
        league = row["league_name"].strip()
        CLUB_TO_LEAGUE[club] = league
        KEYWORD_TO_CLUB[club.lower()] = club

        aliases = CLUB_ALIASES.get(club, [])
        for alias in aliases:
            KEYWORD_TO_CLUB[alias.lower()] = club


    for _, row in df_euro.iterrows():
        club = row["club_name"].strip()
        comp = row["league_name"].strip()
        CLUB_TO_EURO_COMPS.setdefault(club, []).append(comp)

    return KEYWORD_TO_CLUB, CLUB_TO_LEAGUE, CLUB_TO_EURO_COMPS
KEYWORD_TO_CLUB, CLUB_TO_LEAGUE, CLUB_TO_EURO_COMPS= build_keyword_maps("clubs_with_leagues.csv", "european_clubs_in_leagues.csv")

print(CLUB_TO_EURO_COMPS)
