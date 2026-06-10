# vita-mcp-searxng
SearXNG MCP server for VITA — local AI digital human on DGX Spark (GB10)

VITA(ローカルAIデジタルヒューマン)のWeb検索ツールを、MCP (Model Context Protocol) サーバーとして切り出したものです。
キーワードトリガーの密結合ループを、疎結合なMCPインターフェースに置き換える移行の第一弾。

## 構成

- **MCPフレームワーク**: FastMCP (Python)
- **検索バックエンド**: SearXNG (self-hosted, Docker)
- **想定クライアント**: VITA Gateway (GB10-A)

## ステータス

🚧 開発中。動いたら更新します。

開発記録はnoteのマガジンで公開しています:
[ローカルAIデジタルヒューマン](https://note.com/gb10_tsurumitsu/m/m0e4211ba791b)
