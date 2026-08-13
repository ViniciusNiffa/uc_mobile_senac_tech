// statics/js/components.js
// Injeta dinamicamente o header e o footer em todas as páginas.

function getBasePath() {
    const scripts = document.getElementsByTagName('script');
    for (let i = 0; i < scripts.length; i++) {
        if (scripts[i].src.includes('components.js')) {
            return scripts[i].src.replace('/statics/js/components.js', '');
        }
    }
    return '';
}

const basePath = getBasePath();

const headerHTML = `
    <header class="topo">
        <div class="topo__esquerda">
            <a class="topo__marca" href="${basePath}/index.html">
                <img src="${basePath}/statics/img/banners/logo-senac.png" alt="Logo Senac" title="Senac" id="logosenac">
            </a>
            <div class="topo__redes">
                <a href="https://pt-br.facebook.com/" target="_blank" rel="noopener" title="Facebook">
                    <img src="${basePath}/statics/img/icons/facebook.png" alt="Facebook">
                </a>
                <a href="https://twitter.com/login?lang=pt" target="_blank" rel="noopener" title="Twitter">
                    <img src="${basePath}/statics/img/icons/twitter.png" alt="Twitter">
                </a>
                <a href="https://www.linkedin.com/" target="_blank" rel="noopener" title="LinkedIn">
                    <img src="${basePath}/statics/img/icons/linkedin.png" alt="LinkedIn">
                </a>
                <a href="https://www.youtube.com/" target="_blank" rel="noopener" title="YouTube">
                    <img src="${basePath}/statics/img/icons/youtube.png" alt="YouTube">
                </a>
                <a href="https://www.instagram.com/?hl=pt-br" target="_blank" rel="noopener" title="Instagram">
                    <img src="${basePath}/statics/img/icons/instagram.png" alt="Instagram">
                </a>
            </div>
        </div>

        <div class="topo__centro">
            <input type="checkbox" id="bt_menu">
            <label for="bt_menu">&#9776;</label>
            <nav id="menu">
                <ul>
                    <li>
                        <a href="${basePath}/index.html">Início</a>
                    </li>
                    <li>
                        <a href="${basePath}/pages/cursos.html">Cursos</a>
                        <ul>
                            <li><a href="${basePath}/pages/cursoinfo.html">Informática</a></li>
                            <li><a href="${basePath}/pages/cursoredes.html">Redes de Computadores</a></li>
                            <li><a href="${basePath}/pages/cursosistemas.html">Desenvolvimento de Sistemas</a></li>
                            <li><a href="${basePath}/pages/cursoadmin.html">Administração</a></li>
                            <li><a href="${basePath}/pages/cursojogos.html">Programação de Jogos Digitais</a></li>
                        </ul>
                    </li>
                    <li>
                        <a href="${basePath}/pages/localizacao.html">Localização</a>
                    </li>
                </ul>
            </nav>
        </div>

        <div class="topo__direita">
            <div class="topo__usuario" id="topo-usuario">
                <a href="${basePath}/pages/usuario/login.html" title="Entrar" class="btn-usuario-topo" id="btn-header-usuario">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    Entrar
                </a>
            </div>
        </div>
    </header>
`;

const footerHTML = `
    <footer class="rodape">
        <nav class="rodape__menu">
            <ul>
                <li><a href="${basePath}/index.html">Início</a></li>
                <li><a href="${basePath}/pages/cursos.html">Cursos</a></li>
                <li><a href="${basePath}/pages/localizacao.html">Localização</a></li>
            </ul>
        </nav>

        <div class="rodape__divisor"></div>

        <div class="rodape__base">
            <div class="rodape__marca">
                <img src="${basePath}/statics/img/banners/logo-senac.png" alt="Logo Senac" id="logo-rodape">
                <p>&copy; Todos os direitos reservados &mdash; Senac Tech</p>
            </div>

            <div class="rodape__redes">
                <a href="https://pt-br.facebook.com/" target="_blank" rel="noopener" title="Facebook">
                    <img src="${basePath}/statics/img/icons/facebook.png" alt="Facebook">
                </a>
                <a href="https://twitter.com/login?lang=pt" target="_blank" rel="noopener" title="Twitter">
                    <img src="${basePath}/statics/img/icons/twitter.png" alt="Twitter">
                </a>
                <a href="https://www.linkedin.com/" target="_blank" rel="noopener" title="LinkedIn">
                    <img src="${basePath}/statics/img/icons/linkedin.png" alt="LinkedIn">
                </a>
                <a href="https://www.youtube.com/" target="_blank" rel="noopener" title="YouTube">
                    <img src="${basePath}/statics/img/icons/youtube.png" alt="YouTube">
                </a>
                <a href="https://www.instagram.com/?hl=pt-br" target="_blank" rel="noopener" title="Instagram">
                    <img src="${basePath}/statics/img/icons/instagram.png" alt="Instagram">
                </a>
            </div>
        </div>
    </footer>
`;

function atualizarBotaoUsuario() {
    const btn = document.getElementById('btn-header-usuario');
    if (!btn) return;

    // Verifica se já existe token salvo
    const token = localStorage.getItem('senac_token');
    const userStr = localStorage.getItem('senac_user');

    if (token && userStr) {
        try {
            const user = JSON.parse(userStr);
            const destino = user.role === 'admin'
                ? `${basePath}/pages/painel-admin.html`
                : `${basePath}/pages/usuario/painel-usuario.html`;

            btn.href = destino;
            btn.title = 'Meu painel';
            btn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
                ${user.nome || 'Meu painel'}
            `;
        } catch (_) { /* token malformado — ignora */ }
    }
}

function renderComponents() {
    const headerContainer = document.getElementById('header-component');
    const footerContainer = document.getElementById('footer-component');

    if (headerContainer) headerContainer.innerHTML = headerHTML;
    if (footerContainer) footerContainer.innerHTML = footerHTML;

    // Favicon dinâmico
    if (!document.querySelector("link[rel*='icon']")) {
        const link = document.createElement('link');
        link.type = 'image/png';
        link.rel = 'shortcut icon';
        link.href = `${basePath}/statics/img/icons/logo-white.png`;
        document.head.appendChild(link);
    }

    // Atualiza botão de usuário conforme estado de login
    atualizarBotaoUsuario();

    // Adiciona classe .ativo ao menu da página atual
    const currentPath = window.location.pathname;
    const menuLinks = document.querySelectorAll('#menu a');
    
    menuLinks.forEach(link => {
        const linkPath = new URL(link.href).pathname;
        
        // Compara os caminhos. Adiciona suporte para quando a rota for apenas / apontando pro index
        if (currentPath === linkPath || (currentPath.endsWith('/') && linkPath.endsWith('index.html'))) {
            link.classList.add('ativo');
            
            // Se for um link de submenu, destaca também o item pai principal
            const parentLi = link.closest('ul').closest('li');
            if (parentLi) {
                const parentLink = parentLi.querySelector(':scope > a');
                if (parentLink) parentLink.classList.add('ativo');
            }
        }
    });
}

document.addEventListener('DOMContentLoaded', renderComponents);
