# AI Trends Analyzer with SEO Keywords

Python script to fetch trending AI tweets, analyze them with Claude, and get Google keyword metrics via DataForSEO.

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env

# Edit .env and add your API credentials:
# - TWITTER_API_KEY
# - TWITTER_USER_ID
# - CLAUDE_API_KEY
# - DATAFORSEO_LOGIN (get from dataforseo.com)
# - DATAFORSEO_PASSWORD

# Make script executable (optional)
chmod +x main.py
```

**⚠️ Security Note:** Never commit your `.env` file to git! It's already in `.gitignore`.

## Usage

```bash
# Basic usage (defaults: keyword="AI", likes=100)
python3 main.py

# Custom keyword
python3 main.py --keyword "machine learning"

# Custom minimum likes
python3 main.py --likes 50

# Combine both
python3 main.py --keyword "ChatGPT" --likes 200

# Show help
python3 main.py --help
```

### Command-line Arguments

- `--keyword` - Search keyword or term (default: "AI")
- `--likes` - Minimum number of likes required (default: 100)

## What it does

1. **Fetches trending tweets** about AI, machine learning, LLMs
2. **Analyzes with Claude AI** to extract:
   - Main topics/themes
   - Emerging trends
   - Key technologies
   - SEO keyword recommendations
3. **Extracts keywords** from tweets and Claude's analysis
4. **Analyzes with DataForSEO** to get Google metrics:
   - Search volume
   - Competition level
   - Cost-per-click (CPC)
   - Keyword difficulty
5. **Identifies best SEO opportunities** (high volume, low competition)
6. **Saves comprehensive JSON report**

## Output

Creates a timestamped JSON file like `ai_trends_analysis_2025-10-01_14-30-45.json` with:
- Top trending tweets ranked by engagement
- Claude's AI insights
- SEO keyword analysis with search volumes
- Best keyword opportunities
- Hashtag analysis
- Engagement metrics

## Configuration

Edit the script to change:
- Search query
- Number of tweets (max_results)
- Tweet filters (min likes, verified only, etc.)
- Keyword analysis depth
- Location/language for keyword data

## DataForSEO Setup

1. Sign up at https://dataforseo.com/
2. Get your credentials from the dashboard
3. Add them to your `.env` file:
   ```
   DATAFORSEO_LOGIN=your_email@example.com
   DATAFORSEO_PASSWORD=your_api_password
   ```

Note: Script works without DataForSEO (will skip keyword analysis), but you'll get better insights with it.

## Environment Variables

All sensitive credentials are stored in `.env` file:

- `TWITTER_API_KEY` - Your Twitter API key
- `TWITTER_USER_ID` - Your Twitter user ID
- `CLAUDE_API_KEY` - Your Anthropic Claude API key
- `DATAFORSEO_LOGIN` - Your DataForSEO email
- `DATAFORSEO_PASSWORD` - Your DataForSEO password

See `.env.example` for the template.

