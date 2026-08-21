// statics/js/painel-usuario.js
// Carrega e salva os dados do perfil do usuário logado.

document.addEventListener('DOMContentLoaded', async () => {
    const form    = document.getElementById('form-perfil');
    const msgBox  = document.getElementById('mensagem-perfil');
    const btnSair = document.getElementById('btn-logout');

    const inputFoto =
    document.getElementById('upload-foto');

    const imagemPerfil =
    document.getElementById('img-perfil');

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
    if (perfil.foto_perfil && imagemPerfil) {
        imagemPerfil.src =
            `${APP_CONFIG.USER_URL}/uploads/` +
            encodeURIComponent(perfil.foto_perfil);
    }
        const setVal = (id, val) => { const el = document.getElementById(id); if (el && val) el.value = val; };
        setVal('nome', perfil.nome || `${perfil.primeiro_nome || ''} ${perfil.sobrenome || ''}`.trim());
        setVal('email', user.email);
        setVal('telefone', perfil.celular || perfil.telefone || '');
    }

    if (inputFoto) {
    inputFoto.addEventListener(
        'change',
        async () => {
            const arquivo = inputFoto.files[0];

            if (!arquivo) return;

            if (arquivo.size > 5 * 1024 * 1024) {
                exibirMensagem(
                    'A foto deve ter no máximo 5 MB.',
                    'erro'
                );
                inputFoto.value = '';
                return;
            }

            const dadosFoto = new FormData();
            dadosFoto.append('foto', arquivo);

            try {
                const resposta = await fetch(
                    `${APP_CONFIG.USER_URL}` +
                    `/users/${user.id}/photo`,
                    {
                        method: 'POST',
                        headers: {
                            Authorization:
                                `Bearer ${localStorage.getItem(
                                    'senac_token'
                                )}`
                        },
                        body: dadosFoto
                    }
                );

                const resultado =
                    await resposta.json();

                if (!resposta.ok) {
                    throw new Error(
                        resultado.error ||
                        'Não foi possível enviar a foto.'
                    );
                }

                imagemPerfil.src =
                    resultado.foto_url;

                exibirMensagem(
                    'Foto atualizada com sucesso!',
                    'sucesso'
                );

            } catch (erro) {
                exibirMensagem(
                    erro.message,
                    'erro'
                );
            }
        }
    );
}

    // ── Salva alterações ────────────────────────────────────────────
    if (form) {
        form.addEventListener('submit', async (e) => {
            e.preventDefault();
            exibirMensagem('', '');

            const dados = {
                nome:     document.getElementById('nome')?.value.trim(),
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
