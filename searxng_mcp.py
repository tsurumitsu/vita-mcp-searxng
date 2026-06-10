"""SearXNGを共通searchの口(MCP)で包む。口の集約・第一話。

旧Gateway(server.py fetch_web_context)のSearXNG固有の工夫は全部この箱の中:
- language=ja
- ニュース質問 → newsカテゴリ + 鮮度フィルタ(time_range)
- ニュースは publishedDate 降順ソート、日付をtitle末尾に付ける
箱の外(Gateway側)に残るのは検索ゲート・クエリ掃除・結果の文字列整形だけ。
"""
from fastmcp import FastMCP
import httpx

mcp = FastMCP("searxng-search")

SEARXNG_URL = "http://localhost:8080"
LANGUAGE = "ja"
NEWS_TIME_RANGE = "week"  # 古い記事が混ざるのを防ぐ
REQUEST_TIMEOUT = 10

# ニュース系の質問。newsカテゴリで「実際の記事見出し+日付」を取りに行く。
_NEWS_HINT_WORDS = ("ニュース", "速報", "報道", "見出し", "話題")


@mcp.tool()
async def search(query: str, top_k: int = 5) -> list[dict]:
    """Webを検索して関連する結果を共通Result形式で返す"""
    params = {"q": query, "format": "json", "language": LANGUAGE}

    is_news = any(w in query for w in _NEWS_HINT_WORDS)
    if is_news:
        params["categories"] = "news"
        if NEWS_TIME_RANGE:
            params["time_range"] = NEWS_TIME_RANGE

    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
        r = await client.get(f"{SEARXNG_URL}/search", params=params)
        r.raise_for_status()

    # JSON出力が無効だとHTMLが返る → 安全に空で返す
    if "json" not in r.headers.get("content-type", "").lower():
        print("[searxng-mcp] SearXNGがJSONを返しませんでした (JSON出力が無効?)", flush=True)
        return []

    hits = r.json().get("results", []) or []

    # ニュースは新しい順 (publishedDateがある記事を優先・降順)
    if is_news:
        hits = sorted(hits, key=lambda h: h.get("publishedDate") or "", reverse=True)

    out = []
    for h in hits[:top_k]:
        title = (h.get("title") or "").strip()
        content = (h.get("content") or "").strip()
        if not (title or content):
            continue
        # ニュースは公開日をtitleに添える (鮮度をLLMに伝える・旧Gateway挙動の踏襲)
        date = (h.get("publishedDate") or "").strip()
        if date:
            title += f"（{date[:10]}）"
        out.append({
            "title": title,
            "content": content,
            "source": "searxng",
            "uri": (h.get("url") or "").strip(),
            "score": h.get("score", 0.0),
        })
    return out


if __name__ == "__main__":
    # 常駐サービスとしてHTTPで立てる (GatewayはこのURLを叩く)
    mcp.run(transport="http", host="127.0.0.1", port=8024, path="/mcp")
