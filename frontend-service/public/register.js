// 新規登録処理を管理するJavaScript

document.addEventListener('DOMContentLoaded', function() {
    // すでにログイン済みの場合はダッシュボードにリダイレクト
    if (localStorage.getItem('token')) {
        window.location.href = 'dashboard.html';
        return;
    }

    const registerForm = document.getElementById('register-form');
    const errorMessage = document.getElementById('error-message');

    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        
        // エラーメッセージをクリア
        errorMessage.style.display = 'none';
        
        // パスワード確認
        if (password !== confirmPassword) {
            errorMessage.textContent = 'パスワードが一致しません';
            errorMessage.style.display = 'block';
            return;
        }
        
        try {
            // 新規登録APIを呼び出す
            const response = await fetch('/api/v1/auth/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    email: email,
                    password: password
                })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.detail || '登録に失敗しました');
            }
            
            // 登録成功後、ログインページにリダイレクト
            alert('登録が完了しました。ログインしてください。');
            window.location.href = 'index.html';
            
        } catch (error) {
            // エラーメッセージを表示
            errorMessage.textContent = error.message;
            errorMessage.style.display = 'block';
            console.error('登録エラー:', error);
        }
    });
});
