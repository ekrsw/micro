// ダッシュボード処理を管理するJavaScript

document.addEventListener('DOMContentLoaded', function() {
    // ログインしていない場合はログインページにリダイレクト
    const token = localStorage.getItem('token');
    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // ユーザー情報を取得
    const userJson = localStorage.getItem('user');
    let user;
    
    try {
        user = JSON.parse(userJson);
    } catch (e) {
        console.error('ユーザー情報の解析に失敗しました', e);
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
        return;
    }
    
    // ユーザー情報を表示
    document.getElementById('user-username').textContent = user.username;
    document.getElementById('user-username-detail').textContent = user.username;
    document.getElementById('user-id').textContent = user.id;
    document.getElementById('user-status').textContent = user.is_active ? '有効' : '無効';
    document.getElementById('user-admin').textContent = user.is_admin ? '管理者' : '一般ユーザー';
    
    // ログアウトボタンの処理
    document.getElementById('logout-btn').addEventListener('click', function() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'index.html';
    });
    
    // ヘルスチェックボタンの処理
    document.getElementById('check-health-btn').addEventListener('click', async function() {
        try {
            // APIのヘルスチェック
            const apiResponse = await fetch('/api/v1/auth/health');
            const apiData = await apiResponse.json();
            
            document.getElementById('api-status').textContent = apiData.status || '不明';
            document.getElementById('db-status').textContent = apiData.database || '不明';
            
        } catch (error) {
            console.error('ヘルスチェックエラー:', error);
            document.getElementById('api-status').textContent = 'エラー';
            document.getElementById('db-status').textContent = 'エラー';
        }
    });
    
    // ページ読み込み時に自動的にヘルスチェックを実行
    document.getElementById('check-health-btn').click();
    
    // 定期的にトークンの有効性を確認
    async function validateToken() {
        try {
            const response = await fetch('/api/v1/auth/me', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });
            
            if (!response.ok) {
                throw new Error('トークンが無効です');
            }
            
        } catch (error) {
            console.error('トークン検証エラー:', error);
            alert('セッションが切れました。再度ログインしてください。');
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = 'index.html';
        }
    }
    
    // 5分ごとにトークンを検証
    setInterval(validateToken, 5 * 60 * 1000);
});
