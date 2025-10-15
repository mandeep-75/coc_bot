import requests
import json
import os
# === CONFIG ===
API_TOKEN = "-0Kl9a1Rzh-A"     # replace with your actual token
PLAYER_TAG = "#xxxxxxxxxx"
BASE_URL = "https://api.clashofclans.com/v1"

headers = {
    "Authorization": f"Bearer {API_TOKEN}"
}

def fetch_player_data(tag):
    encoded_tag = tag.replace("#", "%23")
    url = f"{BASE_URL}/players/{encoded_tag}"
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return res.json()
    else:
        print("❌ Error fetching data:", res.status_code, res.text)
        return None

def extract_loot_values(player_data):
    loot = {"Gold": 0, "Elixir": 0, "DarkElixir": 0}
    for a in player_data.get("achievements", []):
        if a["name"] == "Gold Grab":
            loot["Gold"] = a["value"]
        elif a["name"] == "Elixir Escapade":
            loot["Elixir"] = a["value"]
        elif a["name"] == "Heroic Heist":
            loot["DarkElixir"] = a["value"]
    return loot

def load_old_data(filename):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return {"Gold": 0, "Elixir": 0, "DarkElixir": 0}

def save_new_data(filename, data):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def main():
    player_data = fetch_player_data(PLAYER_TAG)
    save_new_data("player_ldeoot.json", player_data)
    print(player_data)
    if not player_data:
        return

    new_loot = extract_loot_values(player_data)
    old_loot = load_old_data("player_loot.json")

    diff = {
        "GoldDiff": new_loot["Gold"] - old_loot.get("Gold", 0),
        "ElixirDiff": new_loot["Elixir"] - old_loot.get("Elixir", 0),
        "DarkElixirDiff": new_loot["DarkElixir"] - old_loot.get("DarkElixir", 0)
    }

    print("🏰 Player:", player_data["name"])
    print("Gold Looted:", new_loot["Gold"], f"(+{diff['GoldDiff']})")
    print("Elixir Looted:", new_loot["Elixir"], f"(+{diff['ElixirDiff']})")
    print("Dark Elixir Looted:", new_loot["DarkElixir"], f"(+{diff['DarkElixirDiff']})")

    save_new_data("player_loot.json", new_loot)

    print("\n✅ Data updated in player_loot.json")

if __name__ == "__main__":
    main()
    #not useful
