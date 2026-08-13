// statics/js/valida-recuperar-senha.js
// Lógica da página recuperar-senha.html — solicita código de reset por e-mail.

document.addEventListener('DOMContentLoaded', () => {
    const form   = document.getElementById('form-recuperar-senha');
    const msgBox = document.getElementById('mensagem-recuperar');

    if (!form) return;

    function exibirMensagem(texto, tipo) {
        msgBox.textContent = texto;
        msgBox.className = `mensagem mensagem--${tipo}`;
    }

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        exibirMensagem('', '');

        const email = document.getElementById('email').value.trim();

        if (!email) {
            exibirMensagem('Por favor, informe o e-mail cadastrado.', 'erro');
            return;
        }

        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Enviando...';

        const res = await API.forgotPassword(email);

        btn.disabled = false;
        btn.textContent = 'Enviar código';

        if (res.success) {
            // Guarda o e-mail para a próxima tela não precisar redigitar
            sessionStorage.setItem('senac_reset_email', email);
            exibirMensagem('Código enviado! Verifique seu e-mail e clique em "Já tenho um código".', 'sucesso');
        } else {
            exibirMensagem(res.message || 'Erro ao enviar. Verifique o e-mail e tente novamente.', 'erro');
        }
    });
});
