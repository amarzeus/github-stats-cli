# GitHub Stats CLI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful command-line tool to fetch, analyze, and visualize GitHub user statistics. Perfect for developers, recruiters, and data enthusiasts to gain insights into GitHub profiles.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Features

- Fetch basic user stats (followers, following, repos, etc.)
- Display top repositories sorted by stars
- Easy-to-use CLI interface
- No authentication required (uses public GitHub API)
- Export data in JSON or CSV format
- Generate bar charts for top repositories
- Supports GitHub authentication for higher rate limits and private repos
- Compare stats of multiple users with a table
- Generate HTML dashboards with embedded charts

## Installation

### Option 1: From Source (Recommended for Development)

1. Clone the repository:
   ```
   git clone https://github.com/amarzeus/github-stats-cli.git
   cd github-stats-cli
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Run the tool:
   ```
   python github_stats_cli.py <username>
   ```

### Option 2: Install as Package

1. Install via pip (once published):
   ```
   pip install github-stats-cli
   ```

2. Run the tool:
   ```
   github-stats <username>
   ```

## Configuration

You can create a `config.json` file in the project directory to set default values:

```json
{
    "default_max_repos": 10,
    "default_token": "your_github_token_here",
    "output_format": "text",
    "chart_style": "skyblue"
}
```

Copy `config.json.example` to `config.json` and edit as needed. This allows you to set defaults for max repos, token, etc.

## Usage

### Basic Usage
Fetch stats for a GitHub user:
```
python github_stats_cli.py octocat
```

### Advanced Usage
Limit the number of repositories displayed:
```
python github_stats_cli.py octocat --max-repos 5
```

Output in JSON format:
```
python github_stats_cli.py octocat --json
```

Output in CSV format:
```
python github_stats_cli.py octocat --csv
```

Generate a bar chart of top repositories:
```
python github_stats_cli.py octocat --chart
```

Use GitHub personal access token for authentication:
```
python github_stats_cli.py octocat --token YOUR_GITHUB_TOKEN
```

Compare multiple users:
```
python github_stats_cli.py --compare user1 user2 user3
```

Generate an HTML dashboard:
```
python github_stats_cli.py octocat --html
```

**Note**: To create a GitHub token, go to [GitHub Settings > Developer settings > Personal access tokens](https://github.com/settings/tokens). Select `repo` scope for private repos.

### Output Example
```
GitHub Stats for: octocat
Name: The Octocat
Bio: N/A
Location: San Francisco
Followers: 1234
Following: 567
Public Repos: 89
Public Gists: 12
Account Created: 2011-01-25T18:44:36Z

Top Repositories (by stars):
- Hello-World: 1500 stars, N/A
- Spoon-Knife: 1200 stars, HTML
...
```

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details on how to get started.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
