# vita-mcp-searxng

[SearXNG](https://github.com/searxng/searxng) を [FastMCP](https://github.com/jlowin/fastmcp) で包んだ、シンプルな Web 検索 MCP サーバー。MCP クライアントに `search(query, top_k)` という1つの道具を渡します。SearXNG さえあれば、後述の VITA とは無関係に単体で使えます。

> **VITA とは:** 個人で開発しているローカル完結の AI デジタルヒューマン。VRM アバター＋ローカル LLM / VLM / STT / TTS で構成され、NVIDIA DGX Spark (GB10) 上で推論を動かしています。クラウドに出さず手元で完結するのが方針です。本リポジトリは、その VITA の「Web 検索の口」を MCP サーバーとして独立させた最初の公開パーツです。本文中の **Gateway** は、いつ喋るか・何を見るか・どの道具を使うかを仕切る VITA 本体の制御プロセスを指します。

このサーバーが解こうとしている問題は、VITA 本体側の作りにあります。Web 検索・画面文脈・顔認証といった各機能が、それぞれキーワードで意図検出して毎ターンその文脈をプロンプトに注入する、という密結合な作りになっていて、機能が増えるほど重く・誤爆しやすくなっていました。これを「LLM が必要なときだけ道具を取りに行く」疎結合な MCP インターフェースへ移していく、その第一弾がこのリポジトリです。

検索結果は共通の `Result` 形式（`title / content / source / uri / score`）で返します。SearXNG 固有の工夫（日本語優先、ニュースはニュースカテゴリ＋鮮度フィルタ＋新しい順、見出しに公開日付与）は全部この箱の中に閉じ込めてあるので、呼び出し側（Gateway）は「検索して結果を受け取る」だけで済みます。

## 必要なもの

- Python 3.10+
- 動いている SearXNG（**JSON 出力が有効になっていること**。下記参照）
- `fastmcp` / `httpx`（`pip install fastmcp httpx`）

実行場所は問わない。SearXNG に HTTP で届く場所ならどこでも。
作者環境では SearXNG と同居する Windows 機。


```bash
pip install fastmcp httpx
```

### SearXNG 側の設定（重要）

SearXNG はデフォルトで JSON 出力が無効です。`settings.yml` に以下を入れて再起動してください。これが無いと API が HTML を返し、このサーバーは空の結果を返します。

```yaml
search:
  formats:
    - html
    - json
```

## 使い方

```bash
python searxng_mcp.py
```

`http://127.0.0.1:8024/mcp` に MCP サーバー（HTTP transport）が立ち上がります。MCP クライアント（Claude Desktop、自作 Gateway など）からこの URL を指定して `search` ツールを呼びます。

### 提供ツール

| ツール | シグネチャ | 説明 |
|---|---|---|
| `search` | `search(query: str, top_k: int = 5) -> list[dict]` | Web を検索し、共通 Result 形式のリストを返す |

戻り値の各要素:

```json
{
  "title": "記事タイトル（ニュースなら末尾に（YYYY-MM-DD））",
  "content": "本文スニペット",
  "source": "searxng",
  "uri": "https://...",
  "score": 0.0
}
```

- クエリに「ニュース・速報・報道・見出し・話題」のいずれかが含まれると、自動でニュースカテゴリ＋鮮度フィルタ（既定: 直近1週間）に切り替わり、公開日の新しい順に並べ替えて返します。
- `score` は SearXNG の生スコアです（0〜1 に正規化していません）。同一検索内での足切り用途を想定しており、検索をまたいだ比較には使わないでください。

## 設定

スクリプト先頭の定数を直接編集します（環境変数化は今後）。

| 定数 | 既定 | 意味 |
|---|---|---|
| `SEARXNG_URL` | `http://localhost:8080` | SearXNG のベース URL |
| `LANGUAGE` | `ja` | 検索言語 |
| `NEWS_TIME_RANGE` | `week` | ニュースの鮮度フィルタ（`day`/`week`/`month`/`year`/空） |
| `REQUEST_TIMEOUT` | `10` | SearXNG へのタイムアウト（秒） |

## ハマりどころ（実機メモ）

VITA 本体に組み込む過程で踏んだもの。同じ構成の人の役に立てば。

- **`fastmcp` を入れたら `pyyaml` が上がる**: 既存環境で `pyyaml` を 5.3.x にピン留めしている依存（例: `reolinkapi`）があると衝突しうる。仮想環境を分けるのが安全。
- **`pip.exe` のパス焼き付き**: venv をフォルダごと移動すると、`Scripts/pip.exe` の中に旧パスが焼き付いていて起動できないことがある。`python -m pip install ...` で `pip.exe` を経由せず回避できる。
- **JSON が返らない**: 上記の SearXNG 設定漏れが原因。`content-type` を見て HTML なら空を返すようにしてあるので、無言で空が返るときはまずここを疑う。

## VITA について

VITA の開発記録は note のマガジンで公開しています。各機能を「いつ・何を・なぜ・どうハマって・どう解決したか」で残した開発ログです。

- 開発ログ: [ローカルAIデジタルヒューマン（note）](https://note.com/gb10_tsurumitsu/m/m0e4211ba791b)

このリポジトリは、VITA の各機能（Web 検索・画面文脈・顔認証・過去会話・RAG など）を共通の口へ載せ替えていく取り組みの第一号です。今後、同じ `search` のように他の機能も MCP として切り出していく予定です。

## ライセンス

MIT
