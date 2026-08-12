// statics/js/components.js

// Função para descobrir dinamicamente o caminho base do projeto.
// Isso evita problemas de rotas quando abrimos o arquivo no Live Server ou direto na pasta (file://).
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
            <div class="topo__usuario">
                <a href="${basePath}/pages/usuario/login.html" title="Acessar / Cadastrar" class="btn-usuario-topo">
                    <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
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
                <p>&copy; Todos os direitos reservados - Senac Tech</p>
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

function renderComponents() {
    const headerContainer = document.getElementById('header-component');
    const footerContainer = document.getElementById('footer-component');

    if (headerContainer) {
        headerContainer.innerHTML = headerHTML;
    }
    
    if (footerContainer) {
        footerContainer.innerHTML = footerHTML;
    }

    // Injetar favicon dinamicamente em todas as páginas
    if (!document.querySelector("link[rel*='icon']")) {
        const link = document.createElement('link');
        link.type = 'image/png';
        link.rel = 'shortcut icon';
        link.href = `${basePath}/statics/img/icons/logo-white.png`;
        document.getElementsByTagName('head')[0].appendChild(link);
    }
}

// Executa assim que a página carregar
document.addEventListener('DOMContentLoaded', renderComponents);
