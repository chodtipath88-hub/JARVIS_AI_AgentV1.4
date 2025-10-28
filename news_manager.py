import requests

class NewsManager:
    def __init__(self, api_key):
        self.api_key = api_key
        self.cache = []

    def fetch_top_headlines(self, country="th", num=5):
        url = (
            f"https://newsapi.org/v2/top-headlines?"
            f"country={country}&pageSize={num}&apiKey={self.api_key}"
        )
        try:
            resp = requests.get(url)
            data = resp.json()
            articles = data.get("articles", [])
            headlines = []
            for art in articles:
                title = art.get("title")
                url = art.get("url")
                if title:
                    headlines.append(f"{title} — {url}")
            self.cache = headlines
            return headlines
        except Exception as e:
            print("❌ ดึงข่าวล้มเหลว:", e)
            return self.cache # ถ้า fail ให้แสดงข่าวเก่า (cache)

    def get_cached(self):
        return self.cache.copy()