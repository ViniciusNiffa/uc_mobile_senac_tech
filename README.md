# Senac Tech

Projeto escolar (SENAC) de um sistema de divulgação e matrícula em cursos técnicos, com um front-end estático (HTML/CSS/JS) e um back-end de autenticação em Flask.

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

## Front-end

Site estático (sem framework), aberto direto pelo navegador ou por um live server. Os links entre páginas são relativos, então basta abrir `index.html`.

## Back-end (auth_service)

API em Flask que expõe login, cadastro, recuperação de senha e verificação de e-mail em `/api/auth/*` (ver `services/auth_service/app/routes.py`).

### Configuração

1. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
2. Crie um arquivo `.env` dentro de `services/auth_service/` com pelo menos:
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
   ou diretamente:
   ```
   cd services/auth_service
   python run.py
   ```

O front-end assume a API rodando em `http://127.0.0.1:5000/api/auth` (configurável em `statics/js/config.js`).

## Status

O front-end está em processo de redesign (ver `statics/pdf/design-system-referencia.pdf` para a paleta de cores e diretrizes visuais usadas como referência).
