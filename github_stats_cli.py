#!/usr/bin/env python3
"""
GitHub Stats CLI: A simple tool to fetch and display GitHub user statistics.
"""

import argparse
import csv
import io
import json
import matplotlib.pyplot as plt
import os
import requests
import sqlite3
import time
from datetime import datetime
from tabulate import tabulate
from tqdm import tqdm
import yaml
from typing import Dict, Any

CACHE_FILE = ".cache.json"
CACHE_EXPIRY = 3600  # 1 hour

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def init_database():
    """Initialize SQLite database for historical data."""
    conn = sqlite3.connect('github_stats.db')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            date TEXT NOT NULL,
            followers INTEGER,
            following INTEGER,
            public_repos INTEGER,
            public_gists INTEGER
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repo_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            repo_name TEXT NOT NULL,
            date TEXT NOT NULL,
            stars INTEGER,
            forks INTEGER,
            open_issues INTEGER,
            language TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_user_stats_to_db(username: str, data: Dict[str, Any]):
    """Save user stats to database."""
    init_database()
    conn = sqlite3.connect('github_stats.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO user_stats (username, date, followers, following, public_repos, public_gists)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        username,
        datetime.now().isoformat(),
        data.get('followers', 0),
        data.get('following', 0),
        data.get('public_repos', 0),
        data.get('public_gists', 0)
    ))
    
    conn.commit()
    conn.close()

def save_repo_stats_to_db(username: str, repos: list):
    """Save repository stats to database."""
    init_database()
    conn = sqlite3.connect('github_stats.db')
    cursor = conn.cursor()
    
    for repo in repos:
        cursor.execute('''
            INSERT INTO repo_stats (username, repo_name, date, stars, forks, open_issues, language)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            username,
            repo.get('name', ''),
            datetime.now().isoformat(),
            repo.get('stargazers_count', 0),
            repo.get('forks_count', 0),
            repo.get('open_issues_count', 0),
            repo.get('language', '')
        ))
    
    conn.commit()
    conn.close()

def get_user_history(username: str, days: int = 30):
    """Get historical user stats."""
    init_database()
    conn = sqlite3.connect('github_stats.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT date, followers, following, public_repos, public_gists
        FROM user_stats
        WHERE username = ?
        ORDER BY date DESC
        LIMIT ?
    ''', (username, days))
    
    history = cursor.fetchall()
    conn.close()
    return history

def get_cached_data(key, max_age=CACHE_EXPIRY):
    cache = load_cache()
    if key in cache:
        data, timestamp = cache[key]
        if time.time() - timestamp < max_age:
            return data
    return None

def set_cached_data(key, data):
    cache = load_cache()
    cache[key] = (data, time.time())
    save_cache(cache)

def get_user_stats(username: str, token: str = None) -> Dict[str, Any]:
    """Fetch basic user statistics from GitHub API."""
    cache_key = f"user_{username}_{token or 'no_token'}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    url = f"https://api.github.com/users/{username}"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        raise ValueError(f"User '{username}' not found on GitHub.")
    elif response.status_code == 403:
        raise ValueError("API rate limit exceeded. Try again later or use a personal access token.")
    elif response.status_code != 200:
        raise ValueError(f"Failed to fetch user data: {response.status_code} - {response.text}")
    data = response.json()
    set_cached_data(cache_key, data)
    return data

def get_org_stats(orgname: str, token: str = None) -> Dict[str, Any]:
    """Fetch basic organization statistics from GitHub API."""
    cache_key = f"org_{orgname}_{token or 'no_token'}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    url = f"https://api.github.com/orgs/{orgname}"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        raise ValueError(f"Organization '{orgname}' not found on GitHub.")
    elif response.status_code == 403:
        raise ValueError("API rate limit exceeded. Try again later or use a personal access token.")
    elif response.status_code != 200:
        raise ValueError(f"Failed to fetch org data: {response.status_code} - {response.text}")
    data = response.json()
    set_cached_data(cache_key, data)
    return data

def get_user_repos(username: str, max_repos: int = 10, token: str = None, since: str = None) -> list:
    """Fetch user's repositories, sorted by stars."""
    cache_key = f"repos_{username}_{max_repos}_{token or 'no_token'}_{since or 'no_since'}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page={max_repos}"
    if since:
        url += f"&since={since}T00:00:00Z"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        raise ValueError(f"User '{username}' not found on GitHub.")
    elif response.status_code == 403:
        raise ValueError("API rate limit exceeded. Try again later or use a personal access token.")
    elif response.status_code != 200:
        raise ValueError(f"Failed to fetch repos: {response.status_code} - {response.text}")
    data = response.json()
    set_cached_data(cache_key, data)
    return data

def get_org_repos(orgname: str, max_repos: int = 10, token: str = None, since: str = None) -> list:
    """Fetch organization's repositories, sorted by stars."""
    cache_key = f"org_repos_{orgname}_{max_repos}_{token or 'no_token'}_{since or 'no_since'}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    url = f"https://api.github.com/orgs/{orgname}/repos?sort=stars&per_page={max_repos}"
    if since:
        url += f"&since={since}T00:00:00Z"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        raise ValueError(f"Organization '{orgname}' not found on GitHub.")
    elif response.status_code == 403:
        raise ValueError("API rate limit exceeded. Try again later or use a personal access token.")
    elif response.status_code != 200:
        raise ValueError(f"Failed to fetch org repos: {response.status_code} - {response.text}")
    data = response.json()
    set_cached_data(cache_key, data)
    return data

def get_repo_contributors(owner: str, repo: str, token: str = None, max_contribs: int = 5) -> list:
    """Fetch top contributors for a repository."""
    cache_key = f"contributors_{owner}_{repo}_{max_contribs}_{token or 'no_token'}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    url = f"https://api.github.com/repos/{owner}/{repo}/contributors?per_page={max_contribs}"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return []
    elif response.status_code == 403:
        return []
    elif response.status_code != 200:
        return []
    data = response.json()
    set_cached_data(cache_key, data)
    return data

def get_commit_activity(owner: str, repo: str, token: str = None) -> list:
    """Fetch commit activity for a repository."""
    cache_key = f"activity_{owner}_{repo}_{token or 'no_token'}"
    cached = get_cached_data(cache_key)
    if cached:
        return cached
    
    url = f"https://api.github.com/repos/{owner}/{repo}/stats/commit_activity"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code == 404:
        return []
    elif response.status_code == 403:
        return []
    elif response.status_code != 200:
        return []
    data = response.json()
    set_cached_data(cache_key, data)
    return data

def get_rate_limit(token: str = None) -> Dict[str, Any]:
    """Get current GitHub API rate limit status."""
    url = "https://api.github.com/rate_limit"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {}
    return response.json()

def display_org_stats(org_data: Dict[str, Any], repos: list, print_flag: bool = True) -> Dict[str, Any]:
    """Display the fetched org stats in a readable format and return data."""
    data = {
        "orgname": org_data['login'],
        "name": org_data.get('name'),
        "description": org_data.get('description'),
        "location": org_data.get('location'),
        "public_members": org_data.get('public_members_count', 0),
        "followers": org_data['followers'],
        "following": org_data['following'],
        "public_repos": org_data['public_repos'],
        "created_at": org_data['created_at'],
        "top_repositories": [
            {
                "name": repo["name"],
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "forks": repo["forks_count"],
                "open_issues": repo["open_issues_count"],
                "updated_at": repo["updated_at"],
                "size": repo.get("size", 0)
            } for repo in repos[:10]
        ]
    }
    
    if print_flag:
        print(f"GitHub Stats for: {data['orgname']} (Organization)")
        print(f"Name: {data['name'] or 'N/A'}")
        print(f"Description: {data['description'] or 'N/A'}")
        print(f"Location: {data['location'] or 'N/A'}")
        print(f"Public Members: {data['public_members']}")
        print(f"Followers: {data['followers']}")
        print(f"Following: {data['following']}")
        print(f"Public Repos: {data['public_repos']}")
        print(f"Created At: {data['created_at']}")
        
        print("\nTop Repositories (by stars):")
        repo_table = [
            ["Name", "Stars", "Language", "Forks", "Open Issues", "Last Updated"]
        ] + [
            [repo["name"], repo["stars"], repo["language"] or "N/A", repo["forks"], repo["open_issues"], repo["updated_at"]]
            for repo in data["top_repositories"]
        ]
        print(tabulate(repo_table, headers="firstrow", tablefmt="grid"))
    
    return data

def display_stats(user_data: Dict[str, Any], repos: list, print_flag: bool = True, show_contributors: bool = False, token: str = None, show_activity: bool = False, show_health: bool = False, show_sizes: bool = False) -> Dict[str, Any]:
    """Display the fetched stats in a readable format and return data."""
    data = {
        "username": user_data['login'],
        "name": user_data.get('name'),
        "bio": user_data.get('bio'),
        "location": user_data.get('location'),
        "followers": user_data['followers'],
        "following": user_data['following'],
        "public_repos": user_data['public_repos'],
        "public_gists": user_data['public_gists'],
        "created_at": user_data['created_at'],
        "top_repositories": [
            {
                "name": repo["name"],
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "forks": repo["forks_count"],
                "open_issues": repo["open_issues_count"],
                "updated_at": repo["updated_at"],
                "size": repo.get("size", 0)
            } for repo in repos[:10]
        ]
    }
    
    if print_flag:
        print(f"GitHub Stats for: {data['username']}")
        print(f"Name: {data['name'] or 'N/A'}")
        print(f"Bio: {data['bio'] or 'N/A'}")
        print(f"Location: {data['location'] or 'N/A'}")
        print(f"Followers: {data['followers']}")
        print(f"Following: {data['following']}")
        print(f"Public Repos: {data['public_repos']}")
        print(f"Public Gists: {data['public_gists']}")
        print(f"Account Created: {data['created_at']}")
        
        print("\nTop Repositories (by stars):")
        headers = ["Name", "Stars", "Language", "Forks", "Open Issues", "Last Updated"]
        if show_health:
            headers.append("Health Score")
        if show_sizes:
            headers.append("Size (KB)")
        repo_table = [headers]
        for repo in data["top_repositories"]:
            row = [repo["name"], repo["stars"], repo["language"] or "N/A", repo["forks"], repo["open_issues"], repo["updated_at"]]
            if show_health:
                # Simple health score calculation
                health = repo["stars"] * 2 + repo["forks"] * 3 - repo["open_issues"]
                # Bonus for recent updates (within 30 days)
                from datetime import datetime, timezone
                try:
                    updated = datetime.fromisoformat(repo["updated_at"].replace('Z', '+00:00'))
                    days_since = (datetime.now(timezone.utc) - updated).days
                    if days_since <= 30:
                        health += 10
                except:
                    pass
                row.append(health)
            if show_sizes:
                row.append(repo["size"])
            repo_table.append(row)
        print(tabulate(repo_table, headers="firstrow", tablefmt="grid"))
        
        if show_contributors and repos:
            top_repo = repos[0]
            contributors = get_repo_contributors(data['username'], top_repo['name'], token)
            if contributors:
                print(f"\nTop Contributors for {top_repo['name']}:")
                contrib_table = [
                    ["Username", "Contributions"]
                ] + [
                    [contrib["login"], contrib["contributions"]]
                    for contrib in contributors[:5]
                ]
                print(tabulate(contrib_table, headers="firstrow", tablefmt="grid"))
        
        if show_activity and repos:
            top_repo = repos[0]
            activity = get_commit_activity(data['username'], top_repo['name'], token)
            if activity:
                print(f"\nCommit Activity for {top_repo['name']} (last 52 weeks):")
                total_commits = sum(week['total'] for week in activity)
                print(f"Total Commits: {total_commits}")
                recent_weeks = activity[-12:]  # Last 12 weeks
                activity_table = [
                    ["Week", "Commits"]
                ] + [
                    [f"Week {i+1}", week['total']]
                    for i, week in enumerate(recent_weeks)
                ]
                print(tabulate(activity_table, headers="firstrow", tablefmt="grid"))
    
    # Save to database
    save_user_stats_to_db(data['username'], data)
    save_repo_stats_to_db(data['username'], repos)
    
    return data

def output_csv(data: Dict[str, Any]):
    """Output data in CSV format."""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # User stats
    writer.writerow(["Type", "Username", "Name", "Bio", "Location", "Followers", "Following", "Public Repos", "Public Gists", "Created At"])
    writer.writerow(["User", data["username"], data["name"], data["bio"], data["location"], data["followers"], data["following"], data["public_repos"], data["public_gists"], data["created_at"]])
    
    # Repos
    writer.writerow([])
    writer.writerow(["Type", "Name", "Stars", "Language", "Forks", "Open Issues", "Last Updated"])
    for repo in data["top_repositories"]:
        writer.writerow(["Repo", repo["name"], repo["stars"], repo["language"], repo["forks"], repo["open_issues"], repo["updated_at"]])
    
    print("CSV Output:")
    print(output.getvalue())

def output_yaml(data: Dict[str, Any]):
    """Output data in YAML format."""
    yaml_output = yaml.dump(data, default_flow_style=False, allow_unicode=True)
    print("YAML Output:")
    print(yaml_output)

def generate_chart(data: Dict[str, Any]):
    """Generate a bar chart of top repositories by stars."""
    repos = data["top_repositories"]
    if not repos:
        print("No repositories to chart.")
        return
    
    names = [repo["name"] for repo in repos]
    stars = [repo["stars"] for repo in repos]
    
    plt.figure(figsize=(10, 6))
    plt.bar(names, stars, color='skyblue')
    plt.xlabel('Repository')
    plt.ylabel('Stars')
    plt.title(f'Top Repositories by Stars for {data["username"]}')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig('github_stats_chart.png')
    print("Chart saved as 'github_stats_chart.png'")

def generate_html(data: Dict[str, Any]):
    """Generate an HTML dashboard."""
    html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GitHub Stats Dashboard - {data["username"]}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        h1 {{ color: #333; }}
        .stats {{ display: flex; flex-wrap: wrap; }}
        .stat {{ background: #f4f4f4; padding: 10px; margin: 10px; border-radius: 5px; flex: 1; min-width: 200px; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>GitHub Stats Dashboard for {data["username"]}</h1>
    <div class="stats">
        <div class="stat"><strong>Name:</strong> {data.get("name", "N/A")}</div>
        <div class="stat"><strong>Bio:</strong> {data.get("bio", "N/A")}</div>
        <div class="stat"><strong>Location:</strong> {data.get("location", "N/A")}</div>
        <div class="stat"><strong>Followers:</strong> {data["followers"]}</div>
        <div class="stat"><strong>Following:</strong> {data["following"]}</div>
        <div class="stat"><strong>Public Repos:</strong> {data["public_repos"]}</div>
        <div class="stat"><strong>Public Gists:</strong> {data["public_gists"]}</div>
        <div class="stat"><strong>Account Created:</strong> {data["created_at"]}</div>
    </div>
    <h2>Top Repositories</h2>
    <table>
        <tr><th>Name</th><th>Stars</th><th>Language</th><th>Forks</th><th>Open Issues</th><th>Last Updated</th></tr>
        {"".join(f"<tr><td>{repo['name']}</td><td>{repo['stars']}</td><td>{repo['language'] or 'N/A'}</td><td>{repo['forks']}</td><td>{repo['open_issues']}</td><td>{repo['updated_at']}</td></tr>" for repo in data["top_repositories"])}
    </table>
    <!-- If chart exists, embed it -->
    <h2>Chart</h2>
    <img src="github_stats_chart.png" alt="Repository Stars Chart" style="max-width: 100%;">
</body>
</html>
"""
    with open("github_stats_dashboard.html", "w") as f:
        f.write(html)
    print("Dashboard saved as 'github_stats_dashboard.html'")

def generate_pie_chart(data: Dict[str, Any]):
    """Generate a pie chart of programming languages."""
    repos = data["top_repositories"]
    if not repos:
        print("No repositories to chart.")
        return
    
    languages = {}
    for repo in repos:
        lang = repo["language"] or "Others"
        languages[lang] = languages.get(lang, 0) + 1
    
    labels = list(languages.keys())
    sizes = list(languages.values())
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title(f'Programming Languages Distribution for {data["username"]}')
    plt.axis('equal')
    plt.savefig('github_languages_pie.png')
    print("Pie chart saved as 'github_languages_pie.png'")

def compare_users(usernames: list, token: str = None, max_repos: int = 10):
    """Compare stats of multiple users."""
    user_data_list = []
    with tqdm(total=len(usernames), desc="Fetching user data") as pbar:
        for username in usernames:
            try:
                user_data = get_user_stats(username, token)
                repos = get_user_repos(username, max_repos, token)
                data = display_stats(user_data, repos, False)  # Don't print individual
                user_data_list.append(data)
                pbar.set_postfix_str(f"Processed {username}")
            except ValueError as e:
                print(f"Error fetching data for {username}: {e}")
                return
            pbar.update(1)
    
    # Create comparison table
    headers = ["Stat"] + usernames
    table = [
        ["Name", *[d.get("name", "N/A") for d in user_data_list]],
        ["Followers", *[d["followers"] for d in user_data_list]],
        ["Following", *[d["following"] for d in user_data_list]],
        ["Public Repos", *[d["public_repos"] for d in user_data_list]],
        ["Public Gists", *[d["public_gists"] for d in user_data_list]],
        ["Account Created", *[d["created_at"] for d in user_data_list]],
    ]
    print("\nUser Comparison:")
    print(tabulate(table, headers=headers, tablefmt="grid"))

def main():
    # Load config
    config = {}
    if os.path.exists("config.json"):
        with open("config.json", "r") as f:
            config = json.load(f)
    
    parser = argparse.ArgumentParser(description="Fetch GitHub user statistics.")
    parser.add_argument("username", nargs='?', help="GitHub username to fetch stats for (use --compare for multiple)")
    parser.add_argument("--max-repos", type=int, default=config.get("default_max_repos", 10), help="Max number of repos to display (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--csv", action="store_true", help="Output in CSV format")
    parser.add_argument("--chart", action="store_true", help="Generate a bar chart of top repositories by stars")
    parser.add_argument("--token", default=config.get("default_token", ""), help="GitHub personal access token for authentication (optional)")
    parser.add_argument("--compare", nargs='+', help="Compare stats of multiple users")
    parser.add_argument("--html", action="store_true", help="Generate an HTML dashboard")
    parser.add_argument("--pie", action="store_true", help="Generate a pie chart of programming languages")
    parser.add_argument("--org", help="Get stats for organization instead of user")
    parser.add_argument("--since", help="Filter repos updated since date (YYYY-MM-DD)")
    parser.add_argument("--contributors", action="store_true", help="Show top contributors for the top repository")
    parser.add_argument("--activity", action="store_true", help="Show commit activity for top repositories")
    parser.add_argument("--yaml", action="store_true", help="Output in YAML format")
    parser.add_argument("--rate-limit", action="store_true", help="Show current GitHub API rate limit status")
    parser.add_argument("--health", action="store_true", help="Calculate and display repository health scores")
    parser.add_argument("--web", action="store_true", help="Launch web interface")
    parser.add_argument("--history", type=int, nargs='?', const=30, help="Show historical data for last N days (default 30)")
    parser.add_argument("--sizes", action="store_true", help="Show repository sizes and file counts")
    args = parser.parse_args()
    
    if args.rate_limit:
        rate_limit_data = get_rate_limit(args.token)
        if rate_limit_data:
            core = rate_limit_data.get('resources', {}).get('core', {})
            print("GitHub API Rate Limit Status:")
            print(f"Limit: {core.get('limit', 'N/A')}")
            print(f"Remaining: {core.get('remaining', 'N/A')}")
            print(f"Reset Time: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(core.get('reset', 0)))}")
        else:
            print("Unable to fetch rate limit information.")
        return
    
    if args.web:
        print("Launching web interface...")
        print("Open http://localhost:5000 in your browser")
        from web_app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        return
    
    is_org = False
    if args.compare:
        usernames = args.compare
    elif args.org:
        usernames = [args.org]
        is_org = True
    elif args.username:
        usernames = [args.username]
        is_org = False
    else:
        parser.error("Either provide a username, --org organization, or use --compare for multiple users")
    
    if args.history:
        history = get_user_history(usernames[0], args.history)
        if history:
            print(f"Historical data for {usernames[0]} (last {args.history} days):")
            history_table = [
                ["Date", "Followers", "Following", "Public Repos", "Public Gists"]
            ] + [
                [datetime.fromisoformat(entry[0]).strftime('%Y-%m-%d'), entry[1], entry[2], entry[3], entry[4]]
                for entry in history
            ]
            print(tabulate(history_table, headers="firstrow", tablefmt="grid"))
        else:
            print(f"No historical data found for {usernames[0]}")
        return
    
    try:
        if len(usernames) > 1:
            compare_users(usernames, args.token, args.max_repos)
        else:
            if is_org:
                org_data = get_org_stats(usernames[0], args.token)
                repos = get_org_repos(usernames[0], args.max_repos, args.token, args.since)
                data = display_org_stats(org_data, repos, not (args.json or args.csv or args.chart or args.html or args.pie))
            else:
                user_data = get_user_stats(usernames[0], args.token)
                repos = get_user_repos(usernames[0], args.max_repos, args.token, args.since)
                data = display_stats(user_data, repos, not (args.json or args.csv or args.chart or args.html or args.pie or args.yaml), args.contributors, args.token, args.activity, args.health, args.sizes)
            if args.json:
                print(json.dumps(data, indent=4))
            if args.csv:
                output_csv(data)
            if args.yaml:
                output_yaml(data)
            if args.chart:
                generate_chart(data)
            if args.html:
                generate_html(data)
            if args.pie:
                generate_pie_chart(data)
    except ValueError as e:
        print(f"Error: {e}")
    except requests.RequestException as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    main()
