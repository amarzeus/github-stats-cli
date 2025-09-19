#!/usr/bin/env python3
"""
GitHub Stats CLI: A simple tool to fetch and display GitHub user statistics.
"""

import argparse
import json
import requests
from typing import Dict, Any

def get_user_stats(username: str) -> Dict[str, Any]:
    """Fetch basic user statistics from GitHub API."""
    url = f"https://api.github.com/users/{username}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch user data: {response.status_code} - {response.text}")
    return response.json()

def get_user_repos(username: str, max_repos: int = 10) -> list:
    """Fetch user's repositories, sorted by stars."""
    url = f"https://api.github.com/users/{username}/repos?sort=stars&per_page={max_repos}"
    response = requests.get(url)
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch repos: {response.status_code} - {response.text}")
    return response.json()

def display_stats(user_data: Dict[str, Any], repos: list, json_flag: bool = False) -> Dict[str, Any]:
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
    
    if not json_flag:
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

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub user statistics.")
    parser.add_argument("username", help="GitHub username to fetch stats for")
    parser.add_argument("--max-repos", type=int, default=10, help="Max number of repos to display (default: 10)")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    args = parser.parse_args()
    
    try:
        user_data = get_user_stats(args.username)
        repos = get_user_repos(args.username, args.max_repos)
        data = display_stats(user_data, repos, args.json)
        if args.json:
            print(json.dumps(data, indent=4))
    except ValueError as e:
        print(f"Error: {e}")
    except requests.RequestException as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    main()
