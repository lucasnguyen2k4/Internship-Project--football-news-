import os
import json
import re
from datetime import datetime, timezone
from collections import defaultdict, Counter
from dateutil import parser
from dateutil.tz import tzoffset
from keywords_match import build_keyword_maps  

BLOCKLIST = [
    "rugby", "atp", "tennis", "boxing", "mma", "ufc", "fighting", "ring",
    "golf", "cricket", "basketball", "nba", "mlb", "nfl", "baseball", "horse racing",
    "cycling", "olympics", "hockey", "ice hockey", "wrestling", "f1", "motogp",
    "snooker", "badminton", "volleyball", "darts", "table tennis", "handball", "swimming", "weight", "wta",
    "grand slam", "match point", "set point", "opening round", "madrid open", "australian open",
    "wimbledon", "us open", "french open", "roland garros", "pga tour", "gold cup", "ipl", "racing", "wsl", "woman",
    "women", "china open", "rbc heritage", "driver"
]

GENERAL_FOOTBALL_WORDS = [
    "football", "soccer", "match", "goal", "golden goal", "manager",
    "player", "coach", "transfer", "signs", "joins", "defeats", "beats",
    "cup", "final", "semi-final", "semi-finals", "quarter-final", "quarter-finals", "fa cup", "premier league",
    "champions league", "europa league", "super cup", "derby", "draw",
    "title", "retention", "promotion", "relegation", "kickoff", "stadium"
]

def convert_to_utc7(date_str):
    try:
        dt = parser.parse(date_str)
    except Exception:
        print(f" Failed parse date: {date_str}")
        return None
    if dt.tzinfo:
        return dt.astimezone(tzoffset("UTC+7", 7 * 3600))
    return dt.replace(tzinfo=timezone.utc).astimezone(tzoffset("UTC+7", 7 * 3600))

def is_football_article(article, keyword_to_club):
    text = (article.get("title", "") + " " + article.get("summary", "")).lower()
    url = article.get("url", "").lower()
    combined = f"{text} {url}"
    if any(blocked in combined for blocked in BLOCKLIST):
        return False
    if any(word in combined for word in GENERAL_FOOTBALL_WORDS):
        return True
    if any(keyword in combined for keyword in keyword_to_club):
        return True
    return False

def detect_clubs_and_leagues(text, url, keyword_to_club, club_to_league, club_to_euro):
    text_lower = text.lower()
    url_lower = url.lower()
    full_text = text_lower + " " + url_lower

    found_clubs = []
    domestic_leagues = []
    found_leagues = set()

    def is_valid_keyword(keyword, club_name):
        if keyword == "hearts" and "heart of midlothian" not in text_lower:
            return False
        return True

    for keyword, club in keyword_to_club.items():
        if re.search(rf"\b{re.escape(keyword)}\b", text_lower):
            if is_valid_keyword(keyword, club):
                found_clubs.append(club)
                league = club_to_league.get(club)
                if league:
                    domestic_leagues.append(league)

    uefa_comps = {
        "uefa champions league": "UEFA Champions League 2024/25",
        "champions league": "UEFA Champions League 2024/25",
        "uefa europa league": "UEFA Europa League 2024/25",
        "europa league": "UEFA Europa League 2024/25",
        "uefa europa conference league": "UEFA Europa Conference League 2024/25",
        "conference league": "UEFA Europa Conference League 2024/25"
    }

    context_words = [
        "win", "beat", "match", "tie", "semi-final", "quarter-final", "advance",
        "progress", "clash", "remontada", "eliminate", "knockout", "draw", "leg", "aggregate"
    ]

    qualifying_phrases = [
    "race for", "fight for", "battle for", "chase for", "push for",
    "aim for", "qualify for", "qualification to", "hope to qualify"
]

    def is_qualification_context(phrase, full_text):
        return any(qp in full_text for qp in qualifying_phrases) and phrase in full_text

    mentioned_uefa = {
        league for phrase, league in uefa_comps.items()
        if phrase in full_text
        and any(w in full_text for w in context_words)
        and not is_qualification_context(phrase, full_text)
    }

    if len(found_clubs) >= 2:
        euro_sets = [set(club_to_euro.get(club, [])) for club in found_clubs]
        common_euro = set.intersection(*euro_sets)
        found_leagues = common_euro or mentioned_uefa or set(domestic_leagues)
    elif mentioned_uefa:
        found_leagues = mentioned_uefa
    else:
        league_mentions = {lg for lg in domestic_leagues if lg.lower() in text_lower}
        found_leagues = league_mentions or set(domestic_leagues)

    if not found_clubs and not found_leagues:
        if "premier league" in text_lower:
            found_leagues = {"English Premier League 2024/25"}
        elif "la liga" in text_lower:
            found_leagues = {"Spain Primera División 2024/25"}
        elif "serie a" in text_lower:
            found_leagues = {"Italian Serie A 2024/25"}
        elif "bundesliga" in text_lower:
            found_leagues = {"Deutsche Bundesliga 2024/25"}
        elif "ligue 1" in text_lower:
            found_leagues = {"French Ligue 1 2024/25"}

    league_hints = {
        "premier-league": "English Premier League 2024/25",
        "la-liga": "Spain Primera División 2024/25",
        "serie-a": "Italian Serie A 2024/25",
        "bundesliga": "Deutsche Bundesliga 2024/25",
        "ligue-1": "French Ligue 1 2024/25",
        "champions-league": "UEFA Champions League 2024/25",
        "europa-league": "UEFA Europa League 2024/25",
        "conference-league": "UEFA Europa Conference League 2024/25"
    }

    for keyword, league in league_hints.items():
        if keyword in url_lower:
            if league.startswith("UEFA") and not found_leagues:
                found_leagues = {league}
            elif not league.startswith("UEFA"):
                if mentioned_uefa and league in domestic_leagues:
                    found_leagues = {league}
                    mentioned_uefa = set()
                else:
                    found_leagues = found_leagues or {league}
            break

    return list(set(found_clubs)), list(found_leagues)

def clean_and_reorganize(folder_path, output_path):
    print(f" Processing folder: {folder_path}")
    KEYWORD_TO_CLUB, CLUB_TO_LEAGUE, CLUB_TO_EURO_COMPS = build_keyword_maps()

    if not os.path.exists(output_path):
        os.makedirs(output_path)
        print(f" Created directory: {output_path}")

    all_by_date = defaultdict(list)

    for file_name in os.listdir(folder_path):
        if not file_name.endswith(".json"):
            continue

        file_path = os.path.join(folder_path, file_name)
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                articles = json.load(f)
        except Exception as e:
            print(f" Skipping file {file_name}: {e}")
            continue

        for article in articles:
            if not is_football_article(article, KEYWORD_TO_CLUB):
                continue

            dt = convert_to_utc7(article.get("date", ""))
            if not dt:
                continue
            cutoff_date = datetime(2025, 4, 17, tzinfo=tzoffset("UTC+7", 7 * 3600))
            if dt < cutoff_date:
                continue
            article["date"] = dt.isoformat() 
            text = article.get("title", "") + " " + article.get("summary", "")
            url = article.get("url", "") 
            clubs, leagues = detect_clubs_and_leagues(text, url, KEYWORD_TO_CLUB, CLUB_TO_LEAGUE, CLUB_TO_EURO_COMPS)
            article["clubs"] = clubs
            article["leagues"] = leagues
            domestic_leagues = [lg for lg in leagues if not lg.startswith("UEFA")]
            if domestic_leagues:
                for club in clubs:
                    league = CLUB_TO_LEAGUE.get(club)
                    if league in domestic_leagues:
                        article["main_league"] = league
                        break
            true_date = dt.date().isoformat()
            all_by_date[true_date].append(article)

    for date_str, articles in all_by_date.items():
        unique_articles = []
        seen = set()
        for article in articles:
            identifier = (article.get("title"), article.get("source"))
            if identifier not in seen:
                unique_articles.append(article)
                seen.add(identifier)

        unique_articles.sort(key=lambda x: x["date"])
        out_file = os.path.join(output_path, f"{date_str}.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(unique_articles, f, indent=2, ensure_ascii=False)
        print(f" Saved {len(unique_articles)} articles to {out_file} (Dropped {len(articles) - len(unique_articles)} duplicates)")

if __name__ == "__main__":
    INPUT_DIR = "data/rss_by_day"
    OUTPUT_DIR = "data/rss_clean_final"
    clean_and_reorganize(INPUT_DIR, OUTPUT_DIR)
