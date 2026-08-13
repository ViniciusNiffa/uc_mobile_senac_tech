// statics/js/auth-guard.js

// Este script deve ser incluído em páginas que exigem que o usuário esteja logado 
// (ex: painel-usuario.html, painel-admin.html) e também nas páginas de autenticação
// (para evitar que quem já está logado veja o form de login).

document.addEventListener('DOMContentLoaded', () => {
    const currentPath = window.location.pathname;
    const isAuthPage = currentPath.includes('login.html') || currentPath.includes('cadastro.html');
    
    // Se a API ainda não tiver sido carregada por algum motivo
    if (typeof API === 'undefined') {
        console.error("API não carregada. O auth-guard precisa do api.js.");
        return;
    }

    if (!API.isAuthenticated()) {
        // Se NÃO está logado, mas está tentando acessar uma página restrita
        if (!isAuthPage) {
            console.log("Acesso negado. Redirecionando para login.");
            
            // Tenta descobrir o caminho correto para o login.html
            // Se a url contém '/pages/usuario/', login.html está na mesma pasta.
            // Se a url contém '/pages/', login.html está em 'usuario/login.html'
            let pathToLogin = 'login.html';
            if (currentPath.includes('/pages/painel-admin.html')) {
                pathToLogin = 'usuario/login.html';
            }
            
            window.location.href = pathToLogin;
        }
    } else {
        // Se JÁ está logado
        const user = API.getUser();
        
        // Regra 1: Impedir de ver a página de login/cadastro
        if (isAuthPage) {
            if (user && user.role === 'admin') {
                window.location.href = '../painel-admin.html';
            } else {
                window.location.href = 'painel-usuario.html';
            }
            return;
        }
        
        // Regra 2: Impedir usuário comum de acessar o painel de admin
        if (currentPath.includes('painel-admin.html') && user && user.role !== 'admin') {
            alert('Acesso negado. Apenas administradores podem acessar esta página.');
            window.location.href = 'usuario/painel-usuario.html';
        }
    }
});
