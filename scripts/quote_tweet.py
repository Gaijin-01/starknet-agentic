#!/usr/bin/env python3
"""Quote tweet using GraphQL with cookie auth."""

import os
import sys
import json
import httpx

AUTH_TOKEN = os.environ.get("AUTH_TOKEN", "")
CT0 = os.environ.get("CT0", "")

if len(sys.argv) < 3:
    print("Usage: python quote_tweet.py <tweet_id> <comment>")
    sys.exit(1)

TweetID = sys.argv[1]
Comment = sys.argv[2]

url = "https://x.com/i/api/graphql/9c7-kb-b-H5L5b9c5k9rw/CreateTweet"

payload = {
    "variables": {
        "tweetText": Comment,
        "reply": {"inReplyToTweetId": TweetID, "excludeReplyUserIds": []},
        "media": {"mediaEntities": [], "pendingMediaUploadId": None},
        "withCommunityExpire": False,
        "semanticAnnotation": {"tweetType": "retweet_with_comment"},
        "quoteTweetId": TweetID
    },
    "features": {
        "creator_subscriptions_emoji_tweet_web_enabled": True,
        "tweetypie_unmention_optimization_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "responsive_web_twitter_article_tweet_consumption_enabled": False,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "longform_notetweets_rich_text_read_enabled": True,
        "longform_notetweets_inline_media_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "responsive_web_media_download_video_enabled": False,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_enhance_cards_enabled": False
    },
    "queryId": "9c7-kb-b-H5L5b9c5k9rw"
}

headers = {
    "authorization": f"Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuBaFL3KtsyE5cQJAwOJLwzHMicuq15_8UAFUWhycTbvh0L6VQjjoRyQ7AofQQ1Aw8DqC5vvTKCpQA",
    "x-csrf-token": CT0,
    "cookie": f"auth_token={AUTH_TOKEN}; ct0={CT0}",
    "content-type": "application/json"
}

try:
    resp = httpx.post(url, json=payload, headers=headers, timeout=30)
    print(f"Status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, indent=2))
    else:
        print(f"Error: {resp.text[:500]}")
except Exception as e:
    print(f"Exception: {e}")
