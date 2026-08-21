// statics/js/valida-resetar-senha.js
// Lógica da página resetar-senha.html — redefine a senha direto pelo e-mail (sem código/e-mail).

document.addEventListener('DOMContentLoaded', () => {
    const form   = document.getElementById('form-resetar-senha');
    const msgBox = document.getElementById('mensagem-resetar');

    if (!form) return;

    function exibirMensagem(texto, tipo) {
        msgBox.textContent = texto;
        msgBox.className = `mensagem mensagem--${tipo}`;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        exibirMensagem('', '');

        const email = document.getElementById('email').value.trim();
        const senha = document.getElementById('senha').value;

        if (!email || !senha) {
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

        const res = await API.resetPassword(email, senha);

        btn.disabled = false;
        btn.textContent = 'Redefinir senha';

        if (res.success) {
            exibirMensagem('Senha redefinida com sucesso! Redirecionando para o login...', 'sucesso');
            setTimeout(() => { window.location.href = 'login.html'; }, 1800);
        } else {
            exibirMensagem(res.message || 'Não foi possível redefinir a senha.', 'erro');
        }
    });
});
