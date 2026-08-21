document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('form-editar-usuario');
    const mensagem = document.getElementById('mensagem-edicao');
    const btnCancelar = document.getElementById('btn-cancelar');

    const parametros = new URLSearchParams(window.location.search);
    const usuarioLogado = API.getUser();
    const idDaUrl = parametros.get('id');
    const token = localStorage.getItem('senac_token');

    const adminEditandoUsuario =
        usuarioLogado?.role === 'admin' && idDaUrl;

    const userId = adminEditandoUsuario
        ? idDaUrl
        : usuarioLogado?.id;

    const paginaDeRetorno = adminEditandoUsuario
        ? 'painel-admin.html'
        : 'usuario/painel-usuario.html';

    if (!userId) {
        window.location.href = 'usuario/login.html';
        return;
    }

    btnCancelar.addEventListener('click', () => {
        window.location.href = paginaDeRetorno;
    });

    try {
        const resposta = await fetch(
            `${APP_CONFIG.USER_URL}/users/${userId}`,
            {
                headers: {
                    Authorization: `Bearer ${token}`
                }
            }
        );

        const perfil = await resposta.json();

        if (!resposta.ok) {
            throw new Error(
                perfil.error || 'Não foi possível carregar o usuário.'
            );
        }

        document.getElementById('nome').value = perfil.nome || '';
        document.getElementById('sobrenome').value = perfil.sobrenome || '';
        document.getElementById('usuario').value = perfil.usuario || '';
        document.getElementById('celular').value = perfil.celular || '';
        document.getElementById('data_nasc').value = perfil.data_nasc || '';
        document.getElementById('cpf').value = perfil.cpf || '';
        document.getElementById('rg').value = perfil.rg || '';
        document.getElementById('observacao').value =
            perfil.observacao || '';

    } catch (erro) {
        mensagem.textContent = erro.message;
        mensagem.className =
            'mensagem campo--completo mensagem--erro';
    }

    form.addEventListener('submit', async event => {
        event.preventDefault();

        const dados = {
            nome: document.getElementById('nome').value.trim(),
            sobrenome: document.getElementById('sobrenome').value.trim(),
            usuario: document.getElementById('usuario').value.trim(),
            celular: document.getElementById('celular').value.trim(),
            data_nasc: document.getElementById('data_nasc').value,
            cpf: document.getElementById('cpf').value.trim(),
            rg: document.getElementById('rg').value.trim(),
            observacao:
                document.getElementById('observacao').value.trim()
        };

        try {
            const resposta = await fetch(
                `${APP_CONFIG.USER_URL}/users/${userId}`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        Authorization: `Bearer ${token}`
                    },
                    body: JSON.stringify(dados)
                }
            );

            const resultado = await resposta.json();

            if (!resposta.ok) {
                throw new Error(
                    resultado.error ||
                    'Não foi possível atualizar o usuário.'
                );
            }

            mensagem.textContent = 'Usuário atualizado com sucesso!';
            mensagem.className =
                'mensagem campo--completo mensagem--sucesso';

            setTimeout(() => {
                window.location.href = paginaDeRetorno;
            }, 1000);

        } catch (erro) {
            mensagem.textContent = erro.message;
            mensagem.className =
                'mensagem campo--completo mensagem--erro';
        }
    });
});