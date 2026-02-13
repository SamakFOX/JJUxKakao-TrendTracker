import requests
from typing import List, Dict, Optional
from config.settings import settings

def get_trending_videos(max_results: int = 8) -> List[Dict]:
    """
    YouTube Data API를 사용하여 한국의 인기 급상승 영상을 가져옵니다.
    """
    if not settings.YOUTUBE_API_KEY:
        return []

    url = "https://www.googleapis.com/youtube/v3/videos"
    params = {
        "part": "snippet,statistics",
        "chart": "mostPopular",
        "regionCode": "KR",
        "maxResults": max_results,
        "key": settings.YOUTUBE_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        videos = []
        for item in data.get("items", []):
            snippet = item.get("snippet", {})
            videoId = item.get("id")
            videos.append({
                "id": videoId,
                "title": snippet.get("title", ""),
                "thumbnail": snippet.get("thumbnails", {}).get("high", {}).get("url", ""),
                "channelTitle": snippet.get("channelTitle", ""),
                "publishedAt": snippet.get("publishedAt", ""),
                "viewCount": item.get("statistics", {}).get("viewCount", "0")
            })
        return videos
    except Exception as e:
        print(f"[경고] 유튜브 인기 영상 로드 실패: {e}")
        return []
