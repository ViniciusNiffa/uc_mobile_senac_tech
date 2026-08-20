// statics/js/api.js
// Camada de serviços — centraliza todas as chamadas HTTP ao back-end.
// Os métodos de login e register usam MOCK temporário enquanto o back-end
// ainda está sendo finalizado. Os demais já chamam endpoints reais.

const API = {

    // ─── Autenticação ────────────────────────────────────────────────

    async register(userData) {
        try {
            const response = await fetch(
                `${APP_CONFIG.AUTH_URL}/register`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(userData)
                }
            );
    
            return await response.json();
    
        } catch (error) {
            console.error('Erro ao cadastrar:', error);
    
            return {
                success: false,
                message: 'Erro de conexão com o servidor.'
            };
        }
    },

    async login(email, password) {
        try {
            const response = await fetch(
                `${APP_CONFIG.AUTH_URL}/login`,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        email,
                        senha: password
                    })
                }
            );
    
            const data = await response.json();
    
            if (data.success && data.access_token) {
                localStorage.setItem(
                    'senac_token',
                    data.access_token
                );
    
                localStorage.setItem(
                    'senac_refresh',
                    data.refresh_token || ''
                );
    
                localStorage.setItem(
                    'senac_user',
                    JSON.stringify(data.user)
                );
            }
    
            return data;
    
        } catch (error) {
            console.error('Erro ao fazer login:', error);
    
            return {
                success: false,
                message: 'Erro de conexão com o servidor.'
            };
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
