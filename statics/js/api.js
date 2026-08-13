// statics/js/api.js
// Camada de serviços — centraliza todas as chamadas HTTP ao back-end.
// Os métodos de login e register usam MOCK temporário enquanto o back-end
// ainda está sendo finalizado. Os demais já chamam endpoints reais.

const API = {

    // ─── Autenticação ────────────────────────────────────────────────

    async register(userData) {
        try {
            // TODO: substituir mock pelo fetch real quando o back-end estiver rodando:
            // const res = await fetch(`${APP_CONFIG.AUTH_URL}/register`, {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify(userData)
            // });
            // return await res.json();

            console.log('[Mock] Cadastro:', userData);
            await new Promise(r => setTimeout(r, 700));
            return { success: true, message: 'Cadastro realizado!', id: 99 };
        } catch (err) {
            console.error('Erro ao cadastrar:', err);
            return { success: false, message: 'Erro de conexão com o servidor.' };
        }
    },

    async login(email, password) {
        try {
            // TODO: substituir mock pelo fetch real:
            // const res = await fetch(`${APP_CONFIG.AUTH_URL}/login`, {
            //     method: 'POST',
            //     headers: { 'Content-Type': 'application/json' },
            //     body: JSON.stringify({ email, password })
            // });
            // const data = await res.json();
            // if (data.access_token) {
            //     localStorage.setItem('senac_token', data.access_token);
            //     localStorage.setItem('senac_refresh', data.refresh_token || '');
            //     localStorage.setItem('senac_user', JSON.stringify(data.user));
            // }
            // return data;

            console.log('[Mock] Login:', email);
            await new Promise(r => setTimeout(r, 700));

            if (email === 'admin@senac.br' && password === 'admin123') {
                const user = { id: 1, role: 'admin', nome: 'Administrador' };
                localStorage.setItem('senac_token', 'mock_admin_token');
                localStorage.setItem('senac_user', JSON.stringify(user));
                return { success: true, user };
            } else if (email && password.length >= 6) {
                const user = { id: 2, role: 'user', nome: email.split('@')[0] };
                localStorage.setItem('senac_token', 'mock_user_token');
                localStorage.setItem('senac_user', JSON.stringify(user));
                return { success: true, user };
            }
            return { success: false, message: 'E-mail ou senha inválidos.' };
        } catch (err) {
            console.error('Erro ao fazer login:', err);
            return { success: false, message: 'Erro de conexão com o servidor.' };
        }
    },

    // Verificação de e-mail (OTP pós-cadastro)
    async verifyEmail(usuarioId, codigo) {
        try {
            const res = await fetch(`${APP_CONFIG.AUTH_URL}/verify-email`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ usuario_id: usuarioId, codigo })
            });
            return await res.json();
        } catch (err) {
            console.error('Erro ao verificar e-mail:', err);
            return { success: false, message: 'Erro de conexão.' };
        }
    },

    // Reenviar OTP de verificação
    async resendOtp(usuarioId) {
        try {
            const res = await fetch(`${APP_CONFIG.AUTH_URL}/resend-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ usuario_id: usuarioId })
            });
            return await res.json();
        } catch (err) {
            console.error('Erro ao reenviar OTP:', err);
            return { success: false, message: 'Erro de conexão.' };
        }
    },

    // Solicitar código de reset de senha
    async forgotPassword(email) {
        try {
            const res = await fetch(`${APP_CONFIG.AUTH_URL}/forgot-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email })
            });
            return await res.json();
        } catch (err) {
            console.error('Erro ao solicitar reset:', err);
            return { success: false, message: 'Erro de conexão.' };
        }
    },

    // Redefinir senha com código OTP
    async resetPassword(email, codigo, senha) {
        try {
            const res = await fetch(`${APP_CONFIG.AUTH_URL}/reset-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, codigo, senha })
            });
            return await res.json();
        } catch (err) {
            console.error('Erro ao redefinir senha:', err);
            return { success: false, message: 'Erro de conexão.' };
        }
    },

    // ─── Usuário (user_service) ──────────────────────────────────────

    _authHeader() {
        const token = localStorage.getItem('senac_token');
        return token ? { 'Authorization': `Bearer ${token}` } : {};
    },

    async getProfile(userId) {
        try {
            const res = await fetch(`${APP_CONFIG.USER_URL}/users/${userId}`, {
                headers: this._authHeader()
            });
            return await res.json();
        } catch (err) {
            console.error('Erro ao carregar perfil:', err);
            return null;
        }
    },

    async updateProfile(userId, data) {
        try {
            const res = await fetch(`${APP_CONFIG.USER_URL}/users/${userId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json', ...this._authHeader() },
                body: JSON.stringify(data)
            });
            return await res.json();
        } catch (err) {
            console.error('Erro ao atualizar perfil:', err);
            return { success: false, message: 'Erro de conexão.' };
        }
    },

    // ─── Sessão ──────────────────────────────────────────────────────

    logout(redirectPath = '/index.html') {
        localStorage.removeItem('senac_token');
        localStorage.removeItem('senac_refresh');
        localStorage.removeItem('senac_user');
        window.location.href = redirectPath;
    },

    isAuthenticated() {
        return localStorage.getItem('senac_token') !== null;
    },

    getUser() {
        try {
            const u = localStorage.getItem('senac_user');
            return u ? JSON.parse(u) : null;
        } catch (_) {
            return null;
        }
    }
};
