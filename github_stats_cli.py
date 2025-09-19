#!/usr/bin/env python3
"""
GitHub Stats CLI: A simple tool to fetch and display GitHub user statistics.
"""

import argparse
import csv
import io
import json
import matplotlib.pyplot as plt
import requests
from tabulate import tabulate
from typing import Dict, Any

def get_user_stats(username: str, token: str = None) -> Dict[str, Any]:
    """Fetch basic user statistics from GitHub API."""
    url = f"https://api.github.com/users/{username}"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch user data: {response.status_code} - {response.text}")
    return response.json()

def get_user_repos(username: str, max_repos: int = 10, token: str = None) -> list:
    """Fetch user's repositories, sorted by stars."""
    url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page={max_repos}"
    headers = {"Authorization": f"token {token}"} if token else None
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch repos: {response.status_code} - {response.text}")
    return response.json()

def display_stats(user_data: Dict[str, Any], repos: list, print_flag: bool = True) -> Dict[str, Any]:
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
                "name": repo['name'],
                "stars": repo['stargazers_count'],
                "language": repo['language']
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
        if not data['top_repositories']:
            print("No public repositories found.")
        else:
            for repo in data['top_repositories']:
                print(f"- {repo['name']}: {repo['stars']} stars, {repo['language'] or 'N/A'}")
    
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
    writer.writerow(["Type", "Name", "Stars", "Language"])
    for repo in data["top_repositories"]:
        writer.writerow(["Repo", repo["name"], repo["stars"], repo["language"]])
    
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
        <tr><th>Name</th><th>Stars</th><th>Language</th></tr>
        {"".join(f"<tr><td>{repo['name']}</td><td>{repo['stars']}</td><td>{repo['language'] or 'N/A'}</td></tr>" for repo in data["top_repositories"])}
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

def compare_users(usernames: list, token: str = None, max_repos: int = 10):
    """Compare stats of multiple users."""
    user_data_list = []
    for username in usernames:
        try:
            user_data = get_user_stats(username, token)
            repos = get_user_repos(username, max_repos, token)
            data = display_stats(user_data, repos, False)  # Don't print individual
            user_data_list.append(data)
        except ValueError as e:
            print(f"Error fetching data for {username}: {e}")
            return
    
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
    parser = argparse.ArgumentParser(description="Fetch GitHub user statistics.")
    parser.add_argument("username", nargs='?', help="GitHub username to fetch stats for (use --compare for multiple)")
    parser.add_argument("--max-repos", type=int, default=10, help="Max number of repos to display (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    parser.add_argument("--csv", action="store_true", help="Output in CSV format")
    parser.add_argument("--chart", action="store_true", help="Generate a bar chart of top repositories by stars")
    parser.add_argument("--token", help="GitHub personal access token for authentication (optional)")
    parser.add_argument("--compare", nargs='+', help="Compare stats of multiple users")
    parser.add_argument("--html", action="store_true", help="Generate an HTML dashboard")
    args = parser.parse_args()
    
    if args.compare:
        usernames = args.compare
    elif args.username:
        usernames = [args.username]
    else:
        parser.error("Either provide a username or use --compare for multiple users")
    
    try:
        if len(usernames) > 1:
            compare_users(usernames, args.token, args.max_repos)
        else:
            user_data = get_user_stats(usernames[0], args.token)
            repos = get_user_repos(usernames[0], args.max_repos, args.token)
            data = display_stats(user_data, repos, not (args.json or args.csv or args.chart or args.html))
            if args.json:
                print(json.dumps(data, indent=4))
            if args.csv:
                output_csv(data)
            if args.chart:
                generate_chart(data)
            if args.html:
                generate_html(data)
    except ValueError as e:
        print(f"Error: {e}")
    except requests.RequestException as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    main()
