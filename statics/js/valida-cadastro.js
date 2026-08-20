// statics/js/valida-cadastro.js

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('form-cadastro');
    const msgBox = document.getElementById('mensagem-cadastro');

    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Reseta mensagem
        msgBox.textContent = '';
        msgBox.className = 'mensagem campo--completo';

        // Coleta dados dos inputs
        const userData = {
            nome: document.getElementById('nome').value.trim(),
            sobrenome: document.getElementById('sobrenome').value.trim(),
            rua: document.getElementById('rua').value.trim(),
            numero: document.getElementById('numero').value.trim(),
            bairro: document.getElementById('bairro').value.trim(),
            cidade: document.getElementById('cidade').value.trim(),
            estado: document.getElementById('estado').value,
            cep: document.getElementById('cep').value.trim(),
            complemento: document.getElementById('complemento')?.value.trim() || '',
            observacao: document.getElementById('obs')?.value.trim() || '',
            cpf: document.getElementById('cpf').value.trim(),
            rg: document.getElementById('rg').value.trim(),
            data_nasc: document.getElementById('data_nasc').value,
            celular: document.getElementById('celular').value.trim(),
            email: document.getElementById('email').value.trim(),
            usuario: document.getElementById('usuario').value.trim(),
            senha: document.getElementById('senha').value
        };

        // Validação Frontend
        const camposObrigatorios = {
            nome: 'Nome',
            sobrenome: 'Sobrenome',
            rua: 'Rua',
            numero: 'Número',
            bairro: 'Bairro',
            cidade: 'Cidade',
            estado: 'Estado',
            cep: 'CEP',
            cpf: 'CPF',
            rg: 'RG',
            data_nasc: 'Data de Nascimento',
            celular: 'Celular',
            email: 'E-mail',
            usuario: 'Usuário',
            senha: 'Senha'
        };

        for (let key in camposObrigatorios) {
            if (!userData[key]) {
                exibirMensagem(`Por favor, preencha o campo ${camposObrigatorios[key]}.`, 'erro');
                // Foca no primeiro campo vazio
                document.getElementById(key)?.focus();
                return;
            }
        }
        
        if (userData.senha.length < 6) {
            exibirMensagem('A senha deve ter pelo menos 6 caracteres.', 'erro');
            document.getElementById('senha').focus();
            return;
        }

        // Bloqueia botão durante requisição
        const btnSubmit = form.querySelector('button[type="submit"]');
        const btnOriginalText = btnSubmit.textContent;
        btnSubmit.disabled = true;
        btnSubmit.textContent = 'Cadastrando...';

        // Chama a camada de Serviços (API)
        const response = await API.register(userData);

        btnSubmit.disabled = false;
        btnSubmit.textContent = btnOriginalText;

        if (response.success) {
            // Salva o ID retornado para a tela de verificação de e-mail usar
            if (response.id) sessionStorage.setItem('senac_verificar_id', response.id);

            exibirMensagem('Cadastro realizado! Redirecionando para o login...', 'sucesso');

            setTimeout(() => {
                window.location.href = 'login.html';
            }, 1500);
        } else {
            exibirMensagem(response.message, 'erro');
        }
    });

    function exibirMensagem(texto, tipo) {
        msgBox.textContent = texto;
        msgBox.className = `mensagem campo--completo mensagem--${tipo}`;
    }
});
