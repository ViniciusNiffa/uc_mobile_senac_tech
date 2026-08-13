// statics/js/valida-login.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-login');
    const msgBox = document.getElementById('mensagem-login');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reseta mensagem
        msgBox.textContent = '';
        msgBox.className = 'mensagem';

        const email = document.getElementById('email').value.trim();
        const senha = document.getElementById('senha').value;

        // Validação Frontend Básica
        if (!email || !senha) {
            exibirMensagem('Por favor, preencha o e-mail e a senha.', 'erro');
            return;
        }

        // Bloqueia botão durante requisição
        const btnSubmit = form.querySelector('button[type="submit"]');
        const btnOriginalText = btnSubmit.textContent;
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Entrando...';

        // Chama a camada de Serviços (API)
        const response = await API.login(email, senha);

        btnSubmit.disabled = false;
        btnSubmit.textContent = btnOriginalText;

        if (response.success) {
            exibirMensagem('Login realizado com sucesso! Redirecionando...', 'sucesso');
            
            // Redireciona com base no perfil (role)
            setTimeout(() => {
                if (response.user.role === 'admin') {
                    window.location.href = '../painel-admin.html';
                } else {
                    window.location.href = 'painel-usuario.html';
                }
            }, 1000);
        } else {
            exibirMensagem(response.message, 'erro');
        }
    });

    function exibirMensagem(texto, tipo) {
        msgBox.textContent = texto;
        msgBox.className = `mensagem mensagem--${tipo}`;
    }
});
