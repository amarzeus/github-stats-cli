# GitHub Stats CLI

A simple command-line tool to fetch and display GitHub user statistics, including profile info and top repositories. Perfect for developers wanting quick insights into their GitHub presence or others' profiles.

## Features

- Fetch basic user stats (followers, following, repos, etc.)
- Display top repositories sorted by stars
- Easy-to-use CLI interface
- No authentication required (uses public GitHub API)

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

## Requirements

- Python 3.6+
- `requests` library

## Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Ideas for Contributions
- Add graphical output (e.g., charts using matplotlib)
- Support for GitHub API authentication for private repos
- Export stats to JSON/CSV
- Add more detailed repo stats (e.g., forks, issues)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Amar Kumar - [Your GitHub Profile](https://github.com/amarzeus)

## Disclaimer

This tool uses GitHub's public API. Please respect API rate limits and GitHub's terms of service.
