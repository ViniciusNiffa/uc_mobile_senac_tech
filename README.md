# Senac Tech

1° Projeto da UC de Mobile: refazer o sistema do site do Senac com um front-end (HTML/CSS/JS) e um back-end em microsserviços.

## Estrutura do projeto

```
.
├── index.html                  
├── pages/                      
│   ├── cursos.html             
│   ├── cursoinfo.html          
│   ├── cursoredes.html         
│   ├── cursosistemas.html      
│   ├── cursoadmin.html         
│   ├── cursojogos.html         
│   ├── localizacao.html        
│   └── usuario/                
│       ├── cadastro.html
│       ├── login.html
│       ├── perfil.html
│       ├── resetar-senha.html
│       └── sucesso.html
├── statics/
│   ├── css/
│   │   ├── base.css            
│   │   ├── menu.css            
│   │   ├── home.css            
│   │   ├── pages/              
│   │   │   ├── cursos.css
│   │   │   └── curso-detalhe.css
│   │   └── usuario/
│   │       └── usuario.css      
│   ├── js/
│   │   ├── config.js            
│   │   ├── components.js        
│   │   ├── menu.js              
│   │   └── home.js              
│   ├── img/
│   │   ├── banners/             
│   │   └── icons/               
│   └── pdf/                     
└── services/
    └── auth_service/            
        ├── run.py
        └── app/
            ├── routes.py        
            ├── service.py       
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
