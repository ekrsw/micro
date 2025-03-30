FROM python:3.12.9-slim

# 作業ディレクトリの設定
WORKDIR /app/

# 必要な環境変数を設定
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 依存関係のインストール
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションコードのコピー
COPY . /app/

# 非rootユーザーを作成して実行（セキュリティ向上）
RUN adduser --disabled-password --gecos "" appuser && \
    # ボリュームマウントポイントの所有権を変更
    mkdir -p /app/.pytest_cache && \
    chown -R appuser:appuser /app

# Uvicornでアプリケーションを起動（ワーカー数を制限）
# 環境変数からホストとポートを取得するようにエントリポイントスクリプトを使用
COPY ./entrypoint.sh .
RUN chmod +x ./entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]