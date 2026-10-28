# Primeiro passo

## Docker local (Windows / PowerShell)

Abra o Docker Desktop e aguarde o motor Linux ficar disponível. Na pasta deste projeto:

```powershell
Copy-Item .env.example .env
docker compose up --build -d
docker compose --profile tools run --rm seed
```

Abra http://localhost:3000 e http://localhost:8000/docs.
Na interface, mantenha a organização demo e informe o `DEV_TOKEN` do `.env`.
Clique “Carregar fontes”, cadastre outra fonte e envie uma pergunta. O retorno deve indicar
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

## O que exige suas contas

Supabase (projeto e usuário), Google Cloud (OAuth e consentimento), provedor de modelo,
Resend, Asaas e Meta/WhatsApp serão configurados durante os tickets correspondentes.
Nenhuma conta foi criada, nenhuma chave real foi gerada e nada foi publicado.
Não coloque dados reais de clientes na base antes do marco de isolamento e backup.
