# Senac Tech

1° Projeto da UC de Mobile: refazer o sistema do site do Senac com um front-end (HTML/CSS/JS) e um back-end em microsserviços.

## Estrutura do projeto

```
.
├── index.html                  # Página inicial
├── pages/                      # Demais páginas do site
│   ├── cursos.html             # Lista de cursos
│   ├── cursoinfo.html          # Curso: Informática
│   ├── cursoredes.html         # Curso: Redes de Computadores
│   ├── cursosistemas.html      # Curso: Desenvolvimento de Sistemas
│   ├── cursoadmin.html         # Curso: Administração
│   ├── cursojogos.html         # Curso: Programação de Jogos Digitais
│   ├── localizacao.html        # Localização da unidade
│   └── usuario/                # Fluxo de conta do usuário
│       ├── cadastro.html
│       ├── login.html
│       ├── perfil.html
│       ├── recuperar-senha.html
│       ├── resetar-senha.html
│       ├── verificar-email.html
│       └── sucesso.html
├── statics/
│   ├── css/
│   │   ├── base.css            # Reset + layout global (header/nav/footer)
│   │   ├── menu.css            # Menu de navegação (responsivo)
│   │   ├── home.css            # Estilo específico da home
│   │   ├── pages/               # Estilo das páginas de curso
│   │   │   ├── cursos.css
│   │   │   └── curso-detalhe.css
│   │   └── usuario/
│   │       └── usuario.css      # Estilo das páginas de conta
│   ├── js/
│   │   ├── config.js            # URL base da API do auth_service
│   │   ├── components.js        # Chamadas à API (login, cadastro, senha...)
│   │   ├── menu.js              # Destaque do link ativo no menu
│   │   └── home.js              # Comportamento da home (voltar ao topo)
│   ├── img/
│   │   ├── banners/              # Fotos e imagens de curso
│   │   └── icons/                 # Ícones de redes sociais e da UI
│   └── pdf/                       # Documentação de referência (paleta de cores etc.)
└── services/
    └── auth_service/              # API de autenticação (Flask)
        ├── run.py
        └── app/
            ├── routes.py           # Endpoints /api/auth/*
            ├── service.py          # Regras de negócio (login, cadastro, senha, OTP)
            ├── auth.py
            ├── database.py
            └── validator.py
```

### Configuração

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Crie um arquivo `.env` dentro de `services/*_service/` com pelo menos:
   ```
   SECRET_KEY=uma-chave-secreta
   DB_HOST=localhost
   DB_USER=root
   DB_PASS=
   DB_NAME=senac_tech
   ```
3. Rode o serviço:
   ```
   run_all_services.bat
   ```
