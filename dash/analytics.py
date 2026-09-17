"""
dash/analytics.py
─────────────────
Fetches live data from:
  1. Google Analytics 4  — via service account + GA4 Data API
  2. YouTube Data API v3  — via API key (public channel data)
  3. Instagram Graph API  — via long-lived page access token

All functions return plain dicts so the view can pass them straight
to the template. Each function catches its own exceptions and returns
an error key so the template can show a graceful fallback.

─── SETUP REQUIRED ───────────────────────────────────────────────
1. GA4:
   - Create a service account in Google Cloud Console
   - Enable "Google Analytics Data API"
   - Add service account email as Viewer in GA4 → Admin → Access Management
   - Download the JSON key and save to: /root/Big-Story-Networks-India/ga4_service_account.json
   - Set GA4_PROPERTY_ID in settings.py

2. YouTube:
   - Enable "YouTube Data API v3" in Google Cloud Console
   - Create an API Key (no OAuth needed for public channel data)
   - Set YOUTUBE_API_KEY and YOUTUBE_CHANNEL_ID in settings.py

3. Instagram:
   - Create a Meta Developer App
   - Get a long-lived Page Access Token
   - Set INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in settings.py
───────────────────────────────────────────────────────────────────
"""

import json
import requests
from datetime import datetime, timedelta, date

from django.conf import settings


# ─────────────────────────────────────────
#  GOOGLE ANALYTICS 4
# ─────────────────────────────────────────

def fetch_ga4_data():
    """
    Returns last 30 days of GA4 data using the Analytics Data API
    via a service account (no user OAuth needed).
    """
    try:
        from google.analytics.data_v1beta import BetaAnalyticsDataClient
        from google.analytics.data_v1beta.types import (
            RunReportRequest, DateRange, Metric, Dimension, OrderBy
        )
        from google.oauth2 import service_account

        KEY_PATH    = getattr(settings, 'GA4_SERVICE_ACCOUNT_JSON', None)
        PROPERTY_ID = getattr(settings, 'GA4_PROPERTY_ID', None)

        if not KEY_PATH or not PROPERTY_ID:
            return {'error': 'GA4 credentials not configured in settings.py'}

        credentials = service_account.Credentials.from_service_account_file(
            KEY_PATH,
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )
        client = BetaAnalyticsDataClient(credentials=credentials)

        date_range = [DateRange(start_date='30daysAgo', end_date='today')]

        # ── summary metrics ───────────────────────────────────────
        summary_req = RunReportRequest(
            property=f'properties/{PROPERTY_ID}',
            date_ranges=date_range,
            metrics=[
                Metric(name='sessions'),
                Metric(name='totalUsers'),
                Metric(name='screenPageViews'),
                Metric(name='bounceRate'),
                Metric(name='averageSessionDuration'),
                Metric(name='newUsers'),
            ],
        )
        summary_resp = client.run_report(summary_req)
        row = summary_resp.rows[0].metric_values if summary_resp.rows else []

        def mv(i): return row[i].value if row else '0'

        summary = {
            'sessions':          int(mv(0)),
            'users':             int(mv(1)),
            'pageviews':         int(mv(2)),
            'bounce_rate':       round(float(mv(3)) * 100, 1),
            'avg_session_sec':   int(float(mv(4))),
            'new_users':         int(mv(5)),
        }
        # format avg session duration as mm:ss
        m, s = divmod(summary['avg_session_sec'], 60)
        summary['avg_session_fmt'] = f'{m}m {s}s'

        # ── daily sessions (last 30 days for sparkline) ───────────
        daily_req = RunReportRequest(
            property=f'properties/{PROPERTY_ID}',
            date_ranges=date_range,
            dimensions=[Dimension(name='date')],
            metrics=[Metric(name='sessions')],
            order_bys=[OrderBy(dimension=OrderBy.DimensionOrderBy(dimension_name='date'))],
        )
        daily_resp  = client.run_report(daily_req)
        daily_sessions = [
            {'date': r.dimension_values[0].value,
             'sessions': int(r.metric_values[0].value)}
            for r in daily_resp.rows
        ]

        # ── top pages ─────────────────────────────────────────────
        pages_req = RunReportRequest(
            property=f'properties/{PROPERTY_ID}',
            date_ranges=date_range,
            dimensions=[Dimension(name='pagePath'), Dimension(name='pageTitle')],
            metrics=[Metric(name='screenPageViews'), Metric(name='sessions')],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='screenPageViews'), desc=True)],
            limit=8,
        )
        pages_resp = client.run_report(pages_req)
        top_pages = [
            {
                'path':     r.dimension_values[0].value,
                'title':    r.dimension_values[1].value[:55] + ('…' if len(r.dimension_values[1].value) > 55 else ''),
                'views':    int(r.metric_values[0].value),
                'sessions': int(r.metric_values[1].value),
            }
            for r in pages_resp.rows
        ]

        # ── traffic sources ───────────────────────────────────────
        sources_req = RunReportRequest(
            property=f'properties/{PROPERTY_ID}',
            date_ranges=date_range,
            dimensions=[Dimension(name='sessionDefaultChannelGroup')],
            metrics=[Metric(name='sessions')],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
            limit=6,
        )
        sources_resp = client.run_report(sources_req)
        total_sessions = summary['sessions'] or 1
        traffic_sources = [
            {
                'channel':  r.dimension_values[0].value,
                'sessions': int(r.metric_values[0].value),
                'pct':      round(int(r.metric_values[0].value) / total_sessions * 100, 1),
            }
            for r in sources_resp.rows
        ]

        # ── top countries ─────────────────────────────────────────
        countries_req = RunReportRequest(
            property=f'properties/{PROPERTY_ID}',
            date_ranges=date_range,
            dimensions=[Dimension(name='country')],
            metrics=[Metric(name='sessions')],
            order_bys=[OrderBy(metric=OrderBy.MetricOrderBy(metric_name='sessions'), desc=True)],
            limit=5,
        )
        countries_resp = client.run_report(countries_req)
        top_countries = [
            {
                'country':  r.dimension_values[0].value,
                'sessions': int(r.metric_values[0].value),
                'pct':      round(int(r.metric_values[0].value) / total_sessions * 100, 1),
            }
            for r in countries_resp.rows
        ]

        return {
            'summary':         summary,
            'daily_sessions':  daily_sessions,
            'top_pages':       top_pages,
            'traffic_sources': traffic_sources,
            'top_countries':   top_countries,
        }

    except ImportError:
        return {'error': 'google-analytics-data package not installed. Run: pip install google-analytics-data'}
    except Exception as e:
        return {'error': str(e)}


# ─────────────────────────────────────────
#  YOUTUBE DATA API v3
# ─────────────────────────────────────────

def fetch_youtube_data():
    """
    Fetches public channel stats + recent videos using YouTube Data API v3.
    Uses a simple API key — no OAuth needed for public channel data.
    For analytics (views per day, watch time) you need YouTube Analytics API
    with OAuth. This version uses the Data API for channel + video stats.
    """
    try:
        API_KEY    = getattr(settings, 'YOUTUBE_API_KEY', None)
        CHANNEL_ID = getattr(settings, 'YOUTUBE_CHANNEL_ID', None)

        if not API_KEY or not CHANNEL_ID:
            return {'error': 'YouTube credentials not configured in settings.py'}

        BASE = 'https://www.googleapis.com/youtube/v3'

        # ── channel summary ───────────────────────────────────────
        ch_resp = requests.get(f'{BASE}/channels', params={
            'part':  'snippet,statistics,brandingSettings',
            'id':    CHANNEL_ID,
            'key':   API_KEY,
        }, timeout=10)
        ch_resp.raise_for_status()
        ch_data = ch_resp.json()

        if not ch_data.get('items'):
            return {'error': 'Channel not found. Check YOUTUBE_CHANNEL_ID in settings.py'}

        ch       = ch_data['items'][0]
        stats    = ch['statistics']
        snippet  = ch['snippet']

        summary = {
            'channel_name':       snippet.get('title', ''),
            'channel_thumbnail':  snippet.get('thumbnails', {}).get('default', {}).get('url', ''),
            'subscribers':        int(stats.get('subscriberCount', 0)),
            'total_views':        int(stats.get('viewCount', 0)),
            'total_videos':       int(stats.get('videoCount', 0)),
            'description':        snippet.get('description', '')[:120],
        }

        # ── recent videos (last 10) ───────────────────────────────
        search_resp = requests.get(f'{BASE}/search', params={
            'part':        'snippet',
            'channelId':   CHANNEL_ID,
            'maxResults':  10,
            'order':       'date',
            'type':        'video',
            'key':         API_KEY,
        }, timeout=10)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        video_ids = [item['id']['videoId'] for item in search_data.get('items', []) if 'videoId' in item.get('id', {})]

        top_videos = []
        if video_ids:
            vid_resp = requests.get(f'{BASE}/videos', params={
                'part':  'snippet,statistics,contentDetails',
                'id':    ','.join(video_ids),
                'key':   API_KEY,
            }, timeout=10)
            vid_resp.raise_for_status()
            vid_data = vid_resp.json()

            for v in vid_data.get('items', []):
                vstats   = v.get('statistics', {})
                vsnippet = v.get('snippet', {})
                top_videos.append({
                    'id':           v['id'],
                    'title':        vsnippet.get('title', '')[:60],
                    'thumbnail':    vsnippet.get('thumbnails', {}).get('medium', {}).get('url', ''),
                    'published':    vsnippet.get('publishedAt', '')[:10],
                    'views':        int(vstats.get('viewCount', 0)),
                    'likes':        int(vstats.get('likeCount', 0)),
                    'comments':     int(vstats.get('commentCount', 0)),
                    'url':          f"https://youtube.com/watch?v={v['id']}",
                })

            top_videos.sort(key=lambda x: x['views'], reverse=True)

        return {
            'summary':    summary,
            'top_videos': top_videos,
        }

    except requests.exceptions.RequestException as e:
        return {'error': f'YouTube API request failed: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}


# ─────────────────────────────────────────
#  INSTAGRAM GRAPH API
# ─────────────────────────────────────────

def fetch_instagram_data():
    """
    Fetches Instagram Business account insights using the Graph API.
    Requires:
      - A Facebook Page linked to your Instagram Professional account
      - A long-lived Page Access Token
      - INSTAGRAM_ACCESS_TOKEN and INSTAGRAM_ACCOUNT_ID in settings.py
    """
    try:
        TOKEN      = getattr(settings, 'INSTAGRAM_ACCESS_TOKEN', None)
        ACCOUNT_ID = getattr(settings, 'INSTAGRAM_ACCOUNT_ID', None)

        if not TOKEN or not ACCOUNT_ID:
            return {'error': 'Instagram credentials not configured in settings.py'}

        BASE = 'https://graph.facebook.com/v19.0'

        # ── account summary ───────────────────────────────────────
        acc_resp = requests.get(f'{BASE}/{ACCOUNT_ID}', params={
            'fields':       'name,username,biography,followers_count,follows_count,media_count,profile_picture_url,website',
            'access_token': TOKEN,
        }, timeout=10)
        acc_resp.raise_for_status()
        acc = acc_resp.json()

        if 'error' in acc:
            return {'error': acc['error'].get('message', 'Instagram API error')}

        summary = {
            'name':             acc.get('name', ''),
            'username':         acc.get('username', ''),
            'biography':        acc.get('biography', '')[:120],
            'followers':        acc.get('followers_count', 0),
            'following':        acc.get('follows_count', 0),
            'media_count':      acc.get('media_count', 0),
            'profile_picture':  acc.get('profile_picture_url', ''),
            'website':          acc.get('website', ''),
        }

        # ── account insights (last 30 days) ───────────────────────
        insights_resp = requests.get(f'{BASE}/{ACCOUNT_ID}/insights', params={
            'metric':       'impressions,reach,profile_views,follower_count',
            'period':       'day',
            'since':        int((datetime.now() - timedelta(days=30)).timestamp()),
            'until':        int(datetime.now().timestamp()),
            'access_token': TOKEN,
        }, timeout=10)
        insights_resp.raise_for_status()
        ins_data = insights_resp.json().get('data', [])

        insights = {}
        for metric in ins_data:
            name   = metric['name']
            values = metric.get('values', [])
            total  = sum(v.get('value', 0) for v in values)
            insights[name] = total

        summary['impressions']   = insights.get('impressions', 0)
        summary['reach']         = insights.get('reach', 0)
        summary['profile_views'] = insights.get('profile_views', 0)

        # ── recent media (last 12 posts) ──────────────────────────
        media_resp = requests.get(f'{BASE}/{ACCOUNT_ID}/media', params={
            'fields':       'id,caption,media_type,media_url,thumbnail_url,timestamp,like_count,comments_count,permalink',
            'limit':        12,
            'access_token': TOKEN,
        }, timeout=10)
        media_resp.raise_for_status()
        media_items = media_resp.json().get('data', [])

        recent_media = []
        for m in media_items:
            caption = m.get('caption', '') or ''
            recent_media.append({
                'id':            m.get('id'),
                'caption':       caption[:80] + ('…' if len(caption) > 80 else ''),
                'media_type':    m.get('media_type', ''),
                'media_url':     m.get('media_url') or m.get('thumbnail_url', ''),
                'timestamp':     m.get('timestamp', '')[:10],
                'likes':         m.get('like_count', 0),
                'comments':      m.get('comments_count', 0),
                'permalink':     m.get('permalink', ''),
            })

        return {
            'summary':      summary,
            'recent_media': recent_media,
        }

    except requests.exceptions.RequestException as e:
        return {'error': f'Instagram API request failed: {str(e)}'}
    except Exception as e:
        return {'error': str(e)}