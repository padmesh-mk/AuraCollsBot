import json
import time
import os

VOTES_FILE = "votes.json"


def load_votes():
    """Load votes.json, create if it doesn't exist."""
    if not os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, "w") as f:
            json.dump({}, f, indent=4)
    with open(VOTES_FILE, "r") as f:
        return json.load(f)


def save_votes(data):
    """Save votes.json."""
    with open(VOTES_FILE, "w") as f:
        json.dump(data, f, indent=4)


def get_user_data(user_id):
    """Get user vote data with default values."""
    data = load_votes()
    user = data.get(str(user_id), {})
    if not user:
        user = {
            "votes": 0,
            "last_vote": 0,
            "rank": "N/A"
        }
    else:
        if "last_vote" not in user:
            user["last_vote"] = 0
        user["rank"] = get_user_rank(user_id)
    return user


def update_user_vote(user_id):
    """Increment user's votes and update last_vote + rank."""
    data = load_votes()
    user_id = str(user_id)
    now = int(time.time())
    
    if user_id in data:
        data[user_id]["votes"] += 1
        data[user_id]["last_vote"] = now
    else:
        data[user_id] = {
            "votes": 1,
            "last_vote": now
        }
    
    data[user_id]["rank"] = get_user_rank(user_id)
    save_votes(data)


def get_user_rank(user_id):
    """Return the rank of a user based on votes."""
    data = load_votes()
    sorted_users = sorted(
        data.items(), key=lambda x: x[1].get("votes", 0), reverse=True
    )
    for index, (uid, _) in enumerate(sorted_users, start=1):
        if str(uid) == str(user_id):
            return index
    return "N/A"


def get_leaderboard(top_n=None):
    """Return sorted leaderboard by votes."""
    data = load_votes()
    lb = []
    for user_id, info in data.items():
        lb.append((user_id, {
            "votes": info.get("votes", 0),
            "last_vote": info.get("last_vote", 0),
            "rank": get_user_rank(user_id)
        }))
    lb_sorted = sorted(lb, key=lambda x: x[1]["votes"], reverse=True)
    return lb_sorted[:top_n] if top_n else lb_sorted


def get_last_vote(user_id):
    """Return the last vote timestamp."""
    data = load_votes()
    user = data.get(str(user_id), {})
    return user.get("last_vote", 0)
