from flask import Flask, request, jsonify
import requests
import re
import time
from datetime import datetime, timedelta

app = Flask(__name__)

def fetch_server_url(room_num):
    url = f"https://json.vnres.co/room/{room_num}/detail.json"
    try:
        response = requests.get(url)
        if response.ok:
            match = re.search(r"detail(.*)", response.text)
            if match:
                json_data = match.group(1)
                data = requests.json.loads(json_data)
                if data.get("code") == 200:
                    stream = data.get("data", {}).get("stream", {})
                    return {
                        "m3u8": stream.get("m3u8"),
                        "hdM3u8": stream.get("hdM3u8"),
                    }
    except Exception as e:
        print(f"Error fetching server URL: {e}")
    return {"m3u8": None, "hdM3u8": None}


def fetch_matches(time_data, main_referer):
    url = f"https://json.vnres.co/match/matches_{time_data}.json"
    daily_matches = []

    try:
        response = requests.get(url)
        if response.ok:
            match = re.search(r"matches_\d+(.*)", response.text)
            if match:
                json_data = match.group(1)
                data = requests.json.loads(json_data)
                if data.get("code") == 200:
                    matches = data.get("data", [])
                    current_time_seconds = int(time.time())
                    ten_minutes_later = current_time_seconds + 600

                    for match in matches:
                        try:
                            league_name = match["subCateName"]
                            home_team_name = match["hostName"]
                            home_team_logo = match["hostIcon"]
                            away_team_name = match["guestName"]
                            away_team_logo = match["guestIcon"]

                            match_time = int(match["matchTime"] / 1000)
                            match_status = (
                                "live"
                                if current_time_seconds >= match_time or ten_minutes_later > match_time
                                else "vs"
                            )

                            servers_list = []
                            if match_status == "live":
                                for anchor in match["anchors"]:
                                    server_room = anchor["anchor"]["roomNum"]
                                    stream_data = fetch_server_url(server_room)

                                    if stream_data["m3u8"]:
                                        servers_list.append(
                                            {
                                                "name": "Soco SD",
                                                "stream_url": stream_data["m3u8"],
                                                "referer": main_referer,
                                            }
                                        )
                                    if stream_data["hdM3u8"]:
                                        servers_list.append(
                                            {
                                                "name": "Soco HD",
                                                "stream_url": stream_data["hdM3u8"],
                                                "referer": main_referer,
                                            }
                                        )

                            daily_matches.append(
                                {
                                    "match_time": str(match_time),
                                    "match_status": match_status,
                                    "home_team_name": home_team_name,
                                    "home_team_logo": home_team_logo,
                                    "away_team_name": away_team_name,
                                    "away_team_logo": away_team_logo,
                                    "league_name": league_name,
                                    "servers": servers_list,
                                }
                            )
                        except Exception as e:
                            print(f"Error processing match: {e}")
    except Exception as e:
        print(f"Error fetching matches: {e}")

    return daily_matches


@app.route("/matches", methods=["GET"])
def get_matches():
    main_referer = "https://socolivev.co/"

    current_date = datetime.now()
    match_times = [
        (current_date - timedelta(days=1)).strftime("%Y%m%d"),
        current_date.strftime("%Y%m%d"),
        (current_date + timedelta(days=1)).strftime("%Y%m%d"),
    ]

    all_matches = []
    for time_data in match_times:
        all_matches.extend(fetch_matches(time_data, main_referer))

    return jsonify(all_matches), 200


@app.errorhandler(404)
def not_found(error):
    return "Not Found", 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=True)