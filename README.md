# マイクロサービスアーキテクチャプロジェクト

このプロジェクトは、マイクロサービスアーキテクチャを使用して構築されています。各サービスは独立して開発、デプロイ、スケールが可能です。

## 技術スタック

- **FastAPI**: 高性能なPythonウェブフレームワーク
- **SQLAlchemy**: Pythonの人気ORM
- **PostgreSQL**: リレーショナルデータベース
- **JWT認証**: JWTを使用したユーザー認証
- **Alembic**: データベースマイグレーション
- **Docker & Docker Compose**: コンテナ化とオーケストレーション

## サービス構成

### 認証サービス (auth-service)

- ユーザー登録・ログイン機能
- JWTトークン生成・検証
- ポート: 8000

### ユーザープロファイルサービス (user-service)

- ユーザープロファイル管理
- 認証サービスと連携してユーザー識別
- ポート: 8001

### 商品サービス (product-service)

- 商品情報管理（CRUD操作）
- カテゴリー管理
- 在庫管理
- ポート: 8002

### APIゲートウェイ (gateway-service)

- 各マイクロサービスへのリクエスト転送
- 統一されたAPIエンドポイント提供
- ポート: 8080

## 起動方法

### すべてのサービスを起動

```
docker-compose up -d
```

### 特定のサービスのみ起動

```
docker-compose up -d <service-name>
```

例：`docker-compose up -d auth-api auth-db gateway-api`

## API エンドポイント

APIゲートウェイを経由して、以下のエンドポイントにアクセスできます：

### 認証API

- `POST /api/v1/auth/login/access-token` - ログイン（トークン取得）
- `GET /api/v1/auth/users/me` - 現在のユーザー情報取得

### ユーザープロファイルAPI

- `GET /api/v1/users/profiles/me` - 自分のプロファイル取得
- `PUT /api/v1/users/profiles/me` - 自分のプロファイル更新

### 商品API

- `GET /api/v1/products/products/` - 商品一覧取得
- `POST /api/v1/products/products/` - 商品追加 (管理者のみ)
- `GET /api/v1/products/categories/` - カテゴリー一覧取得

## 開発環境設定

各サービスには独自のdocker-compose.ymlがあり、単独でローカル開発が可能です。

例：
```
cd auth-service
docker-compose up -d
```

## データベースマイグレーション

各サービスでAlembicを使用したマイグレーションを実行する方法：

```
docker-compose exec <service-name> alembic revision --autogenerate -m "メッセージ"
docker-compose exec <service-name> alembic upgrade head
```