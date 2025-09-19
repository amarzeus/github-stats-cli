#!/usr/bin/env python3
"""
GitHub Stats CLI: A simple tool to fetch and display GitHub user statistics.
"""

import argparse
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

def display_stats(user_data: Dict[str, Any], repos: list):
    """Display the fetched stats in a readable format."""
    print(f"GitHub Stats for: {user_data['login']}")
    print(f"Name: {user_data.get('name', 'N/A')}")
    print(f"Bio: {user_data.get('bio', 'N/A')}")
    print(f"Location: {user_data.get('location', 'N/A')}")
    print(f"Followers: {user_data['followers']}")
    print(f"Following: {user_data['following']}")
    print(f"Public Repos: {user_data['public_repos']}")
    print(f"Public Gists: {user_data['public_gists']}")
    print(f"Account Created: {user_data['created_at']}")
    
    print("\nTop Repositories (by stars):")
    if not repos:
        print("No public repositories found.")
    else:
        for repo in repos[:10]:  # Limit to top 10
            print(f"- {repo['name']}: {repo['stargazers_count']} stars, {repo['language'] or 'N/A'}")

def main():
    parser = argparse.ArgumentParser(description="Fetch GitHub user statistics.")
    parser.add_argument("username", help="GitHub username to fetch stats for")
    parser.add_argument("--max-repos", type=int, default=10, help="Max number of repos to display (default: 10)")
    args = parser.parse_args()
    
    try:
        user_data = get_user_stats(args.username)
        repos = get_user_repos(args.username, args.max_repos)
        display_stats(user_data, repos)
    except ValueError as e:
        print(f"Error: {e}")
    except requests.RequestException as e:
        print(f"Network error: {e}")

if __name__ == "__main__":
    main()
