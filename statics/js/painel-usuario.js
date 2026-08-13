// statics/js/painel-usuario.js
// Carrega e salva os dados do perfil do usuário logado.

document.addEventListener('DOMContentLoaded', async () => {
    const form    = document.getElementById('form-perfil');
    const msgBox  = document.getElementById('mensagem-perfil');
    const btnSair = document.getElementById('btn-logout');

    const user = API.getUser();
    if (!user) return; // auth-guard já cuida do redirecionamento

    function exibirMensagem(texto, tipo) {
        if (!msgBox) return;
        msgBox.textContent = texto;
        msgBox.className = `mensagem mensagem--${tipo}`;
    }

    // ── Carrega dados do perfil ─────────────────────────────────────
    const perfil = await API.getProfile(user.id);
    if (perfil && !perfil.error) {
        const setVal = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };
        setVal('nome', perfil.nome || `${perfil.primeiro_nome || ''} ${perfil.sobrenome || ''}`.trim());
        setVal('email', perfil.email);
        setVal('telefone', perfil.celular || perfil.telefone || '');
    }

    // ── Salva alterações ────────────────────────────────────────────
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            exibirMensagem('', '');

            const dados = {
                nome:     document.getElementById('nome')?.value.trim(),
                email:    document.getElementById('email')?.value.trim(),
                telefone: document.getElementById('telefone')?.value.trim(),
            };

            const senha = document.getElementById('senha')?.value;
            if (senha) dados.senha = senha;

            const btn = form.querySelector('button[type="submit"]');
            btn.disabled = true;
            btn.textContent = 'Salvando...';

            const res = await API.updateProfile(user.id, dados);

            btn.disabled = false;
            btn.textContent = 'Salvar Alterações';

            exibirMensagem(
                res.message || (res.error ? res.error : 'Perfil atualizado com sucesso!'),
                res.error ? 'erro' : 'sucesso'
            );
        });
    }

    // ── Logout ──────────────────────────────────────────────────────
    if (btnSair) {
        btnSair.addEventListener('click', () => {
            API.logout('../../index.html');
        });
    }
});
