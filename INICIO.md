# Primeiro passo

## Docker local (Windows / PowerShell)

Abra o Docker Desktop e aguarde o motor Linux ficar disponível. Na pasta deste projeto:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose --profile tools run --rm seed
```

Abra http://localhost:3000/login (a UI chama a API via proxy em `/v1`) e http://localhost:8000/docs.
Após mudar o frontend, rode `docker compose up --build -d web`.
Se `/login` mostrar só **Carregando sessão…** (sem formulário), reconstrua a imagem do web:
`docker compose build --no-cache web` e depois `docker compose up -d web`. O Dockerfile usa `WORKDIR /src`
(deixe de usar `/app` no build) para não confundir o Next com a pasta `app/` do App Router.
Entre com Supabase (quando configurado) ou com o `DEV_TOKEN` do `.env` em development.
Selecione a organização demo, clique “Carregar fontes”, cadastre outra fonte e envie uma pergunta. O retorno deve indicar
`needs_setup`, sem inventar valores da empresa. O cadastro ainda não importa o conteúdo de arquivos.

```powershell
docker compose logs --tail 100 api worker
docker compose down
```

`down` preserva os volumes. Não use `down -v` se quiser preservar seus dados.
O Compose expõe portas somente em localhost; PostgreSQL e Redis não são publicados.
O perfil local utiliza usuário proprietário do banco; não atende ao isolamento forte de produção.

## Backend sem Docker, para desenvolvimento

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e './backend[dev]'
Set-Location backend
$env:DATABASE_URL='sqlite:///./nexo.db'
$env:DEV_AUTH='true'
$env:DEV_TOKEN='local-demo-change-this-token-2026'
alembic upgrade head
python -m app.seed
uvicorn app.main:app --reload
```

SQLite serve apenas para smoke tests do plano de controle. Não valida schemas, pgvector,
RLS, permissões PostgreSQL, fila ou sincronização concorrente.

Em outro terminal, na pasta `frontend`:

```powershell
npm ci
npm run dev
```

## Como continuar com IA

Abra esta pasta no editor, leia `AGENTS.md` e use o prompt Setup de `docs/prompts.md`.
Depois execute os tickets pela ordem de dependência, começando por INF-001 e BE-001.
Faça commits pequenos e revise cada migration antes de aplicá-la.

## Login: e-mail, senha e Google (Supabase)

1. Crie um projeto em [Supabase](https://supabase.com) e copie **Project URL** e **anon key**
   para `.env` (`NEXT_PUBLIC_*` e `SUPABASE_URL` com a mesma URL).
2. No Supabase: **Authentication → Providers → Google** — ative e informe Client ID/Secret
   do [Google Cloud Console](https://console.cloud.google.com/) (OAuth consent + credencial Web).
3. Em **Authentication → URL Configuration**, adicione redirect:
   `http://localhost:3000/auth/callback` (e o domínio de produção depois).
4. No Google Cloud, **Authorized redirect URI** deve incluir o callback do Supabase
   (algo como `https://<projeto>.supabase.co/auth/v1/callback`), não só o do Nexo.
5. **E-mail/senha:** deixe Email provider habilitado; confirmação de e-mail conforme política do projeto.
6. Após o primeiro login, o usuário precisa de **membership** num tenant (seed local só cobre
   `DEV_USER`; usuários Google/e-mail reais exigem convite ou script admin — ver BE-017).

Rebuild do frontend Docker após mudar variáveis `NEXT_PUBLIC_*`:
`docker compose up --build -d web`.

## O que exige suas contas

Supabase (projeto e usuário), Google Cloud (OAuth e consentimento), provedor de modelo,
Resend, Asaas e Meta/WhatsApp serão configurados durante os tickets correspondentes.
Nenhuma conta foi criada, nenhuma chave real foi gerada e nada foi publicado.
Não coloque dados reais de clientes na base antes do marco de isolamento e backup.
