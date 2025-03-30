// ログイン処理を管理するJavaScript

document.addEventListener('DOMContentLoaded', function() {
    // すでにログイン済みの場合はダッシュボードにリダイレクト
    if (localStorage.getItem('token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    const loginForm = document.getElementById('login-form');
    const errorMessage = document.getElementById('error-message');

    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        
        // エラーメッセージをクリア
        errorMessage.style.display = 'none';
        
        try {
            // FormDataオブジェクトを作成（OAuth2の仕様に合わせる）
            const formData = new URLSearchParams();
            formData.append('username', email);  // OAuth2では'username'を使用
            formData.append('password', password);
            
            // ログインAPIを呼び出す
            const response = await fetch('/api/v1/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded'
                },
                body: formData
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || 'ログインに失敗しました');
            }
            
            // トークンをローカルストレージに保存
            localStorage.setItem('token', data.access_token);
            
            // ユーザー情報を取得
            const userResponse = await fetch('/api/v1/auth/me', {
                headers: {
                    'Authorization': `Bearer ${data.access_token}`
                }
            });
            
            if (!userResponse.ok) {
                throw new Error('ユーザー情報の取得に失敗しました');
            }
            
            const userData = await userResponse.json();
            
            // ユーザー情報をローカルストレージに保存
            localStorage.setItem('user', JSON.stringify(userData));
            
            // ダッシュボードページにリダイレクト
            window.location.href = 'dashboard.html';
            
        } catch (error) {
            // エラーメッセージを表示
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
            console.error('ログインエラー:', error);
        }
    });
});
