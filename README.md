# GitHub Follow-Back Automation

This project automatically manages GitHub follows based on the principle: "If you follow me, I follow you and vice versa".

## How it Works

The automation checks your GitHub followers and following lists, then:
- Automatically follows back users who follow you
- Unfollows users who have unfollowed you

This creates a reciprocal following relationship with your GitHub connections.

## Setup

1. See [GITHUB_SETUP.md](GITHUB_SETUP.md) for configuration instructions
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables in `.env`
4. Run with: `python run.py`

## Requirements

- Python 3.x
- GitHub Personal Access Token
- Requirements listed in `requirements.txt`

## Automatic Updates

The automation runs on a schedule via GitHub Actions workflow to keep your follows synchronized.