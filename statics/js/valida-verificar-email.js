// statics/js/valida-verificar-email.js
// Lógica da página verificar-email.html — confirma OTP pós-cadastro.

document.addEventListener('DOMContentLoaded', () => {
    const form    = document.getElementById('form-verificar-email');
    const msgBox  = document.getElementById('mensagem-verificar');
    const btnReenviar = document.getElementById('reenviar-codigo');

    if (!form) return;

    // Recupera o usuario_id gravado pelo valida-cadastro.js após o registro
    const usuarioId = sessionStorage.getItem('senac_verificar_id');

    function exibirMensagem(texto, tipo) {
        msgBox.textContent = texto;
        msgBox.className = `mensagem mensagem--${tipo}`;
    }

    // ── Submit: verifica o código ──────────────────────────────────
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        exibirMensagem('', '');

        const codigo = document.getElementById('codigo').value.trim();

        if (codigo.length !== 6) {
            exibirMensagem('O código deve ter 6 dígitos.', 'erro');
            return;
        }

        if (!usuarioId) {
            exibirMensagem('Sessão expirada. Por favor, faça o cadastro novamente.', 'erro');
            return;
        }

        const btn = form.querySelector('button[type="submit"]');
        btn.disabled = true;
        btn.textContent = 'Verificando...';

        const res = await API.verifyEmail(usuarioId, codigo);

        btn.disabled = false;
        btn.textContent = 'Verificar';

        if (res.success) {
            sessionStorage.removeItem('senac_verificar_id');
            exibirMensagem('E-mail verificado! Redirecionando...', 'sucesso');
            setTimeout(() => { window.location.href = 'sucesso.html'; }, 1200);
        } else {
            exibirMensagem(res.message || 'Código inválido ou expirado.', 'erro');
        }
    });

    // ── Reenviar OTP ───────────────────────────────────────────────
    if (btnReenviar) {
        btnReenviar.addEventListener('click', async (e) => {
            e.preventDefault();
            if (!usuarioId) return;

            btnReenviar.textContent = 'Enviando...';
            const res = await API.resendOtp(usuarioId);
            btnReenviar.textContent = 'Reenviar código';

            exibirMensagem(
                res.success ? 'Código reenviado! Verifique seu e-mail.' : (res.message || 'Erro ao reenviar.'),
                res.success ? 'sucesso' : 'erro'
            );
        });
    }
});
