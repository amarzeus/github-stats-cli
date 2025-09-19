#!/usr/bin/env python3
"""
GitHub Stats CLI Web Interface
A web interface for the GitHub Stats CLI tool.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import sys

# Add the current directory to the path so we can import the CLI functions
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from github_stats_cli import (
    get_user_stats, get_user_repos, display_stats,
    get_org_stats, get_org_repos, display_org_stats,
    compare_users, output_yaml, output_csv
)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'github-stats-web'

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/stats/<username>')
def get_stats(username):
    """API endpoint to get user stats."""
    token = request.args.get('token', '')
    format_type = request.args.get('format', 'json')
    max_repos = int(request.args.get('max_repos', 10))
    since = request.args.get('since', None)
    show_health = request.args.get('health', 'false').lower() == 'true'

    try:
        user_data = get_user_stats(username, token)
        repos = get_user_repos(username, max_repos, token, since)
        data = display_stats(user_data, repos, False, show_health=show_health)

        if format_type == 'yaml':
            return output_yaml(data), 200, {'Content-Type': 'text/plain'}
        elif format_type == 'csv':
            return output_csv(data), 200, {'Content-Type': 'text/csv'}
        else:
            return jsonify(data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/org/<orgname>')
def get_org_stats_api(orgname):
    """API endpoint to get organization stats."""
    token = request.args.get('token', '')
    format_type = request.args.get('format', 'json')
    max_repos = int(request.args.get('max_repos', 10))
    since = request.args.get('since', None)

    try:
        org_data = get_org_stats(orgname, token)
        repos = get_org_repos(orgname, max_repos, token, since)
        data = display_org_stats(org_data, repos, False)

        if format_type == 'yaml':
            return output_yaml(data), 200, {'Content-Type': 'text/plain'}
        elif format_type == 'csv':
            return output_csv(data), 200, {'Content-Type': 'text/csv'}
        else:
            return jsonify(data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/compare')
def compare_users_api():
    """API endpoint to compare multiple users."""
    usernames = request.args.get('users', '').split(',')
    usernames = [u.strip() for u in usernames if u.strip()]
    token = request.args.get('token', '')
    max_repos = int(request.args.get('max_repos', 10))

    if len(usernames) < 2:
        return jsonify({'error': 'At least 2 users required for comparison'}), 400

    try:
        # For API, we'll return the data structure instead of printing
        user_data_list = []
        for username in usernames:
            user_data = get_user_stats(username, token)
            repos = get_user_repos(username, max_repos, token)
            data = display_stats(user_data, repos, False)
            user_data_list.append(data)

        return jsonify({
            'comparison': user_data_list,
            'users': usernames
        })

    except ValueError as e:
        return jsonify({'error': str(e)}), 400

@app.route('/stats/<username>')
def stats_page(username):
    """Web page to display user stats."""
    return render_template('stats.html', username=username)

@app.route('/org/<orgname>')
def org_page(orgname):
    """Web page to display org stats."""
    return render_template('org.html', orgname=orgname)

@app.route('/compare')
def compare_page():
    """Web page for user comparison."""
    return render_template('compare.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
