// statics/js/valida-resetar-senha.js
// Lógica da página resetar-senha.html — valida código OTP e define nova senha.

document.addEventListener('DOMContentLoaded', () => {
    const form   = document.getElementById('form-resetar-senha');
    const msgBox = document.getElementById('mensagem-resetar');

    if (!form) return;

    // Pré-preenche o e-mail se a página anterior gravou em sessionStorage
    const emailSalvo = sessionStorage.getItem('senac_reset_email');
    const inputEmail = document.getElementById('email');
    if (emailSalvo && inputEmail) {
        inputEmail.value = emailSalvo;
    }

    function exibirMensagem(texto, tipo) {
        msgBox.textContent = texto;
        msgBox.className = `mensagem mensagem--${tipo}`;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        exibirMensagem('', '');

        const email  = document.getElementById('email').value.trim();
        const codigo = document.getElementById('codigo').value.trim();
        const senha  = document.getElementById('senha').value;

        if (!email || !codigo || !senha) {
            exibirMensagem('Preencha todos os campos.', 'erro');
            return;
        }

        if (senha.length < 6) {
            exibirMensagem('A nova senha deve ter pelo menos 6 caracteres.', 'erro');
            return;
        }

        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Redefinindo...';

        const res = await API.resetPassword(email, codigo, senha);

        btn.disabled = false;
        btn.textContent = 'Redefinir senha';

        if (res.success) {
            sessionStorage.removeItem('senac_reset_email');
            exibirMensagem('Senha redefinida com sucesso! Redirecionando para o login...', 'sucesso');
            setTimeout(() => { window.location.href = 'login.html'; }, 1800);
        } else {
            exibirMensagem(res.message || 'Código inválido ou expirado. Solicite um novo código.', 'erro');
        }
    });
});
