# Contributing to GitHub Stats CLI

Thank you for your interest in contributing to GitHub Stats CLI! We welcome contributions from the community.

## How to Contribute

### 1. Fork the Repository
Fork the repository on GitHub to your own account.

### 2. Clone Your Fork
```bash
git clone https://github.com/your-username/github-stats-cli.git
cd github-stats-cli
```

### 3. Set Up Development Environment
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 4. Create a Feature Branch
```bash
git checkout -b feature/your-feature-name
```

### 5. Make Your Changes
- Follow the existing code style
- Add tests for new features
- Update documentation as needed
- Ensure all tests pass

### 6. Commit Your Changes
```bash
git add .
git commit -m "Add: Brief description of your changes"
```

### 7. Push to Your Fork
```bash
git push origin feature/your-feature-name
```

### 8. Create a Pull Request
- Go to the original repository on GitHub
- Click "New Pull Request"
- Select your feature branch
- Provide a clear description of your changes

## Development Guidelines

### Code Style
- Use Python 3.6+ compatible code
- Follow PEP 8 style guidelines
- Use meaningful variable and function names
- Add docstrings to functions and classes

### Testing
- Test your changes thoroughly
- Run existing tests to ensure no regressions
- Add unit tests for new functionality

### Documentation
- Update README.md for new features
- Add inline comments for complex logic
- Update type hints for function parameters

## Ideas for Contributions

- **New Export Formats**: Add support for XML, YAML, or other formats
- **Advanced Visualizations**: Implement pie charts, line graphs, or interactive plots
- **API Enhancements**: Add more GitHub API endpoints (e.g., commits, issues)
- **Performance Improvements**: Optimize API calls and data processing
- **Configuration**: Add config file support for default settings
- **Internationalization**: Add support for multiple languages
- **Web Interface**: Create a simple web UI using Flask or similar

## Reporting Issues

If you find a bug or have a feature request:
1. Check existing issues to avoid duplicates
2. Use the issue templates provided
3. Provide clear steps to reproduce bugs
4. Include your environment details (OS, Python version, etc.)

## Code of Conduct

Please be respectful and constructive in all interactions. We aim to foster an inclusive and welcoming community.

## Questions?

If you have questions about contributing, feel free to open an issue or contact the maintainers.
