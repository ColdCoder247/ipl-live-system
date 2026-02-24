import requests
import os
from PIL import Image, ImageDraw, ImageFont
from datetime import datetime

API_KEY = os.getenv("CRICKET_API_KEY")

def load_team_logo(team_name):
    clean_name = team_name.lower().replace(" ", "_")
    path = f"assets/ipl_logos/{clean_name}.png"
    if os.path.exists(path):
        return Image.open(path).convert("RGBA")
    return None

def get_ipl_match():
    url = f"https://api.cricketdata.org/v1/matches?apikey={API_KEY}"
    data = requests.get(url).json()["data"]

    matches = []
    for match in data:
        if match.get("match_type", "").lower() == "t20" and \
           "indian premier league" in match.get("series", "").lower():
            matches.append(match)

    live = [m for m in matches if m["status"].lower() == "live"]
    if live:
        return live[0]

    upcoming = [m for m in matches if m["status"].lower() == "upcoming"]
    upcoming.sort(key=lambda x: x["date"])
    return upcoming[0] if upcoming else None


match = get_ipl_match()

if not match:
    print("No IPL match found")
    exit()

team1 = match["teams"][0]
team2 = match["teams"][1]
status = match["status"]
series = match["series"]

is_live = status.lower() == "live"
is_finished = status.lower() in ["completed", "finished"]

bg = "assets/background_live.png" if is_live else "assets/background_upcoming.png"
img = Image.open(bg).convert("RGBA")
draw = ImageDraw.Draw(img)

font_big = ImageFont.truetype("assets/montserrat.ttf", 80)
font_mid = ImageFont.truetype("assets/montserrat.ttf", 50)

draw.text((200, 120), series.upper(), fill="orange", font=font_mid)
draw.text((200, 250), team1, fill="white", font=font_big)
draw.text((200, 350), "VS", fill="gray", font=font_mid)
draw.text((200, 450), team2, fill="white", font=font_big)

# Logos
logo1 = load_team_logo(team1)
logo2 = load_team_logo(team2)

if logo1:
    logo1 = logo1.resize((150,150))
    img.paste(logo1, (50, 250), logo1)

if logo2:
    logo2 = logo2.resize((150,150))
    img.paste(logo2, (900, 250), logo2)

# LIVE Score
if is_live and match.get("score"):
    score = match["score"][0]
    runs = score["r"]
    wickets = score["w"]
    overs = score["o"]

    run_rate = round(runs / float(overs), 2) if float(overs) > 0 else 0

    draw.text((200, 650), f"{runs}/{wickets}", fill="white", font=font_big)
    draw.text((200, 750), f"Overs: {overs}", fill="white", font=font_mid)
    draw.text((200, 820), f"Run Rate: {run_rate}", fill="yellow", font=font_mid)

# Upcoming
elif not is_live and not is_finished:
    draw.text((200, 650), f"Starts: {match['date']}", fill="white", font=font_mid)

# Finished Banner
if is_finished:
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 180))
    img = Image.alpha_composite(img, overlay)
    draw = ImageDraw.Draw(img)

    draw.text((300, 500), "MATCH FINISHED", fill="yellow", font=font_big)
    draw.text((200, 650), status, fill="white", font=font_mid)

draw.text((200, 950), f"Updated: {datetime.now().strftime('%H:%M')}", fill="gray", font=font_mid)

img.save("output/ipl_match.png")
print("IPL Image Generated")
