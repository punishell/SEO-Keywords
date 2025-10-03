#!/usr/bin/env python3
"""
Fetch trending AI tweets and analyze them with Claude + DataForSEO
"""
import requests
import json
import base64
from datetime import datetime
import sys
import os
import argparse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configuration from environment variables
TWITTER_API_KEY = os.getenv("TWITTER_API_KEY")
TWITTER_USER_ID = os.getenv("TWITTER_USER_ID")
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# DataForSEO credentials
DATAFORSEO_LOGIN = os.getenv("DATAFORSEO_LOGIN")
DATAFORSEO_PASSWORD = os.getenv("DATAFORSEO_PASSWORD")

def fetch_trending_tweets(keyword="AI", min_likes=100):
    """Fetch trending tweets based on keyword and minimum likes
    
    Args:
        keyword: Search keyword/term (default: "AI")
        min_likes: Minimum number of likes required (default: 100)
    """
    print(f"📱 Fetching trending tweets for '{keyword}' with {min_likes}+ likes...")
    
    url = "https://api.twitterapi.io/twitter/tweet/advanced_search"
    headers = {
        "X-API-Key": TWITTER_API_KEY,
        "X-User-Id": TWITTER_USER_ID,
        "Accept": "application/json"
    }
    params = {
        "query": f'({keyword}) min_faves:{min_likes} filter:media',
        "max_results": "10"
    }
    
    try:
        response = requests.get(url, headers=headers, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        tweets = data.get("tweets", [])
        print(f"✅ Fetched {len(tweets)} tweets")
        return tweets
    except Exception as e:
        print(f"❌ Error fetching tweets: {e}")
        return []

def analyze_with_claude(tweets):
    """Send tweets to Claude for analysis"""
    if not tweets:
        print("⚠️  No tweets to analyze")
        return {}
    
    print("🤖 Analyzing with Claude AI...")
    
    # Prepare tweet summary for Claude
    tweet_text = "\n".join([
        f"{i+1}. {tweet.get('text', '')[:200]} "
        f"({tweet.get('likeCount', 0)} likes, "
        f"hashtags: {', '.join(tweet.get('hashtags', [])[:5])})"
        for i, tweet in enumerate(tweets[:10])
    ])
    
    prompt = f"""Analyze these trending AI-related tweets and extract:
1. Main topics/themes (as array)
2. Emerging trends (as array)
3. Key technologies mentioned (as array)
4. Recommended SEO keywords (as array)

Tweets:
{tweet_text}

Return ONLY valid JSON with keys: topics, trends, technologies, keywords
Each should be an array of strings."""

    url = "https://api.anthropic.com/v1/messages"
    headers = {
        "x-api-key": CLAUDE_API_KEY,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json"
    }
    payload = {
        "model": "claude-3-5-sonnet-20241022",
        "max_tokens": 2048,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        result = response.json()
        
        # Extract Claude's response
        content = result.get("content", [{}])[0].get("text", "{}")
        
        # Try to parse JSON from response
        try:
            # Find JSON in the response
            start = content.find("{")
            end = content.rfind("}") + 1
            if start >= 0 and end > start:
                analysis = json.loads(content[start:end])
                print("✅ Claude analysis complete")
                return analysis
            else:
                print("⚠️  Could not find JSON in Claude response")
                return {"raw_response": content}
        except json.JSONDecodeError:
            print("⚠️  Could not parse Claude response as JSON")
            return {"raw_response": content}
            
    except Exception as e:
        print(f"❌ Error calling Claude API: {e}")
        return {}

def extract_keywords_from_tweets(tweets, claude_analysis):
    """Extract unique keywords from tweets and Claude analysis"""
    keywords = set()
    
    # Add hashtags from tweets
    for tweet in tweets:
        hashtags = tweet.get("hashtags", [])
        keywords.update(h.lower() for h in hashtags if h)
    
    # Add keywords from Claude's analysis
    if claude_analysis:
        keywords.update(k.lower() for k in claude_analysis.get("keywords", []))
        keywords.update(t.lower() for t in claude_analysis.get("topics", []))
        keywords.update(tech.lower() for tech in claude_analysis.get("technologies", []))
    
    # Filter and clean
    keywords = [k for k in keywords if len(k) > 2 and len(k) < 50]
    return list(keywords)[:20]  # Limit to top 20 to avoid API costs

def analyze_keywords_with_dataforseo(keywords):
    """Get Google search metrics for keywords using DataForSEO"""
    if not keywords:
        print("⚠️  No keywords to analyze")
        return []
    
    # Skip if credentials not configured
    if DATAFORSEO_LOGIN == "your_email@example.com":
        print("⚠️  DataForSEO credentials not configured, skipping keyword analysis")
        return []
    
    print(f"🔍 Analyzing {len(keywords)} keywords with DataForSEO...")
    
    credentials = base64.b64encode(
        f"{DATAFORSEO_LOGIN}:{DATAFORSEO_PASSWORD}".encode()
    ).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/json"
    }
    
    post_data = [{
        "keywords": keywords,
        "location_name": "United States",
        "language_name": "English",
        "depth": 2,
        "include_serp_info": True
    }]
    
    try:
        response = requests.post(
            "https://api.dataforseo.com/v3/dataforseo_labs/keyword_ideas/live",
            headers=headers,
            json=post_data,
            timeout=60
        )
        response.raise_for_status()
        result = response.json()
        
        # Extract keyword data
        keyword_data = []
        if result.get("tasks"):
            for task in result["tasks"]:
                if task.get("result"):
                    for item in task["result"]:
                        if item.get("items"):
                            for kw in item["items"][:30]:  # Top 30 keywords
                                keyword_data.append({
                                    "keyword": kw.get("keyword"),
                                    "search_volume": kw.get("keyword_info", {}).get("search_volume"),
                                    "competition": kw.get("keyword_info", {}).get("competition"),
                                    "cpc": kw.get("keyword_info", {}).get("cpc"),
                                    "difficulty": kw.get("keyword_properties", {}).get("keyword_difficulty"),
                                })
        
        # Sort by search volume
        keyword_data.sort(key=lambda x: x.get("search_volume", 0) or 0, reverse=True)
        
        print(f"✅ Analyzed {len(keyword_data)} keywords")
        return keyword_data
        
    except Exception as e:
        print(f"❌ Error calling DataForSEO API: {e}")
        return []

def process_tweets(tweets, claude_analysis, dataforseo_keywords):
    """Process and structure the final report"""
    print("📊 Processing results...")
    
    # Extract tweet data
    processed_tweets = []
    all_hashtags = []
    
    for i, tweet in enumerate(tweets[:10]):
        hashtags = tweet.get("hashtags", [])
        all_hashtags.extend(hashtags)
        
        processed_tweets.append({
            "rank": i + 1,
            "text": tweet.get("text", "")[:200],
            "engagement": {
                "likes": tweet.get("likeCount", 0),
                "retweets": tweet.get("retweetCount", 0),
                "score": tweet.get("likeCount", 0) + (tweet.get("retweetCount", 0) * 2)
            },
            "author": tweet.get("author", {}).get("userName", "unknown"),
            "hashtags": hashtags[:5]
        })
    
    # Sort by engagement
    processed_tweets.sort(key=lambda x: x["engagement"]["score"], reverse=True)
    
    # Count hashtag frequency
    hashtag_freq = {}
    for tag in all_hashtags:
        hashtag_freq[tag] = hashtag_freq.get(tag, 0) + 1
    
    top_hashtags = sorted(hashtag_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    
    # Find best keywords (high volume, low-medium competition)
    best_keywords = []
    if dataforseo_keywords:
        for kw in dataforseo_keywords:
            volume = kw.get("search_volume") or 0
            competition = kw.get("competition")
            
            # Calculate opportunity score
            if volume > 0:
                score = volume
                # Apply competition multiplier if available
                if competition is not None and competition < 1.0:
                    score = int(volume * (1 - competition))
                else:
                    score = volume
                
                kw["opportunity_score"] = score
                best_keywords.append(kw)
        
        # Sort by opportunity score
        best_keywords.sort(key=lambda x: x.get("opportunity_score", 0), reverse=True)
    
    # Build final report
    report = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_tweets": len(tweets),
            "unique_hashtags": len(hashtag_freq),
            "total_engagement": sum(t["engagement"]["score"] for t in processed_tweets),
            "keywords_analyzed": len(dataforseo_keywords)
        },
        "ai_insights": {
            "topics": claude_analysis.get("topics", []),
            "emerging_trends": claude_analysis.get("trends", []),
            "key_technologies": claude_analysis.get("technologies", []),
            "recommended_keywords": claude_analysis.get("keywords", [])
        },
        "seo_analysis": {
            "best_opportunities": best_keywords[:10],
            "all_keyword_data": dataforseo_keywords
        },
        "top_trending_tweets": processed_tweets,
        "top_hashtags": [{"tag": tag, "mentions": count} for tag, count in top_hashtags]
    }
    
    return report

def save_report(report):
    """Save report to JSON file"""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"ai_trends_analysis_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"💾 Report saved to: {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error saving report: {e}")
        return None

def print_tweet_details(tweets):
    """Print detailed information about each tweet"""
    print("\n" + "=" * 80)
    print("📱 TWEET DETAILS")
    print("=" * 80)
    
    for i, tweet in enumerate(tweets, 1):
        text = tweet.get("text", "")
        likes = tweet.get("likeCount", 0)
        retweets = tweet.get("retweetCount", 0)
        bookmarks = tweet.get("bookmarkCount", 0)
        author = tweet.get("author", {}).get("userName", "unknown")
        
        print(f"\n[Tweet #{i}]")
        print(f"👤 Author: @{author}")
        print(f"📝 Text: {text[:150]}{'...' if len(text) > 150 else ''}")
        print(f"📊 Engagement:")
        print(f"   ❤️  Likes:     {likes:,}")
        print(f"   🔄 Retweets:  {retweets:,}")
        print(f"   🔖 Bookmarks: {bookmarks:,}")
        print(f"   📈 Total:     {likes + retweets + bookmarks:,}")
        print("-" * 80)

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(
        description='Fetch trending tweets and analyze with Claude + DataForSEO',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        '--keyword',
        type=str,
        default='AI',
        help='Search keyword or term to find tweets about'
    )
    parser.add_argument(
        '--likes',
        type=int,
        default=100,
        help='Minimum number of likes required for tweets'
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 AI Trends Analyzer with SEO Keywords")
    print("=" * 60)
    print(f"🔍 Keyword: '{args.keyword}' | Min Likes: {args.likes}")
    print()
    
    # Step 1: Fetch tweets
    tweets = fetch_trending_tweets(keyword=args.keyword, min_likes=args.likes)
    if not tweets:
        print("❌ No tweets fetched. Exiting.")
        sys.exit(1)
    
    # Print tweet details
    print_tweet_details(tweets)
    
    # Step 2: Analyze with Claude
    claude_analysis = analyze_with_claude(tweets)
    
    # Step 3: Extract keywords and analyze with DataForSEO
    keywords = extract_keywords_from_tweets(tweets, claude_analysis)
    print(f"\n🔑 Extracted keywords: {', '.join(keywords[:10])}")
    
    dataforseo_keywords = analyze_keywords_with_dataforseo(keywords)
    
    # Step 4: Process and structure
    report = process_tweets(tweets, claude_analysis, dataforseo_keywords)
    
    # Step 5: Save to file
    filename = save_report(report)
    
    print()
    print("=" * 60)
    print("✨ Analysis Complete!")
    print("=" * 60)
    print(f"\n📈 Summary:")
    print(f"   • Tweets analyzed: {report['summary']['total_tweets']}")
    print(f"   • Unique hashtags: {report['summary']['unique_hashtags']}")
    print(f"   • Total engagement: {report['summary']['total_engagement']}")
    print(f"   • Keywords analyzed: {report['summary']['keywords_analyzed']}")
    
    if claude_analysis.get("topics"):
        print(f"\n🎯 Top Topics: {', '.join(claude_analysis['topics'][:3])}")
    if claude_analysis.get("trends"):
        print(f"📊 Emerging Trends: {', '.join(claude_analysis['trends'][:3])}")
    
    # Show best keyword opportunities
    best_kws = report.get("seo_analysis", {}).get("best_opportunities", [])
    if best_kws:
        print(f"\n💎 Top Keywords (by volume):")
        for i, kw in enumerate(best_kws[:10], 1):
            vol = kw.get("search_volume")
            comp = kw.get("competition")
            difficulty = kw.get("difficulty")
            
            vol_str = f"{vol:,}" if vol else "N/A"
            comp_str = f"{comp:.2f}" if comp is not None else "N/A"
            diff_str = f"{difficulty}" if difficulty else "N/A"
            
            print(f"   {i}. {kw['keyword']:<40} Search Volume: {vol_str:>10} | Competition: {comp_str:>6} | Difficulty: {diff_str:>6}")
    
    print(f"\n📄 Full report: {filename}")
    print()

if __name__ == "__main__":
    main()

