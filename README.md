# マイクロサービスアーキテクチャ

このプロジェクトは、マイクロサービスアーキテクチャを使用した認証システムの実装例です。

## サービス構成

- **Gateway Service**: Nginx を使用した API ゲートウェイ
- **Auth Service**: FastAPI を使用した認証サービス
- **Database**: PostgreSQL を使用したデータベース

## 技術スタック

- **Gateway Service**:

  - Nginx: リバースプロキシ、ルーティング
  - Docker: コンテナ化

- **Auth Service**:
  - FastAPI: 高速な API フレームワーク
  - SQLAlchemy: ORM とデータベース操作
  - PyJWT: JWT トークン生成と検証
  - Passlib: パスワードハッシュ化
  - PostgreSQL: データベース
  - Docker: コンテナ化

## ディレクトリ構成

```
/
├── docker-compose.yml        # 全サービスのDocker Compose設定
├── gateway-service/          # ゲートウェイサービス
│   ├── Dockerfile
│   ├── nginx.conf            # Nginxのメイン設定
│   └── conf.d/
│       └── default.conf      # プロキシ設定
└── auth-service/             # 認証サービス
    ├── Dockerfile
    ├── requirements.txt      # Pythonの依存関係
    ├── .env                  # 環境変数
    └── app/                  # FastAPIアプリケーション
        ├── main.py           # アプリケーションのエントリーポイント
        ├── api/              # APIエンドポイント
        ├── core/             # 設定と共通機能
        ├── db/               # データベース関連
        ├── models/           # データベースモデル
        └── schemas/          # Pydanticスキーマ
```

## 起動方法

1. リポジトリをクローン:

```bash
git clone <repository-url>
cd <repository-directory>
```

2. Docker Compose でサービスを起動:

```bash
docker-compose up -d
```

3. サービスの確認:

```bash
docker-compose ps
```

## API エンドポイント

### 認証サービス

- **ユーザー登録**: `POST /api/v1/auth/register`

  ```json
  {
    "email": "user@example.com",
    "password": "strongpassword"
  }
  ```

- **ログイン**: `POST /api/v1/auth/login`

  ```json
  {
    "username": "user@example.com",
    "password": "strongpassword"
  }
  ```

- **ユーザー情報取得**: `GET /api/v1/auth/me`
  - ヘッダー: `Authorization: Bearer <token>`

## 開発

### 環境変数

`.env`ファイルで以下の環境変数を設定できます:

- `DATABASE_URL`: データベース接続 URL
- `SECRET_KEY`: JWT トークン生成用の秘密鍵
- `ALGORITHM`: JWT アルゴリズム（デフォルト: HS256）
- `ACCESS_TOKEN_EXPIRE_MINUTES`: アクセストークンの有効期限（分）

## ライセンス

このプロジェクトは MIT ライセンスの下で公開されています。
