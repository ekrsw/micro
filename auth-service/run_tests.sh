#!/bin/bash

# テスト用コンテナの起動とテスト実行
echo "テスト用コンテナを起動してテストを実行します..."
docker-compose -f docker-compose.test.yml up --build --abort-on-container-exit

# テスト終了後のコンテナ停止とクリーンアップ
echo "テスト終了後のクリーンアップを行います..."
docker-compose -f docker-compose.test.yml down -v
