# Desafio Skills — Auditoria e Refatoração Arquitetural

Skill Claude Code que automatiza auditoria e refatoração de projetos legados para arquitetura MVC. Funciona com qualquer stack de backend.

---

## A) Análise Manual

### Projeto 1 — code-smells-project (Python/Flask E-commerce API)

| # | Problema | Severidade | Arquivo:Linha | Relevância |
|---|----------|-----------|---------------|-----------|
| 1 | 18+ pontos de SQL Injection via concatenação de strings | CRITICAL | models.py:28,48,57,68,92,109,126,140,148,157,163,174,188,193,220,224,279,291 | Qualquer usuário pode extrair toda a base, deletar dados ou bypassar autenticação com `' OR '1'='1'` |
| 2 | SECRET_KEY hardcoded no código-fonte | CRITICAL | app.py:7 | Permite forjar tokens de sessão. Impossível rotacionar sem deploy |
| 3 | Endpoint `/admin/query` executa SQL arbitrário sem autenticação | CRITICAL | app.py:59-78 | Shell remoto no banco de dados para qualquer chamador HTTP |
| 4 | Senhas armazenadas em texto puro | CRITICAL | models.py:122-131 | Violação completa de credenciais na primeira exposição do banco |
| 5 | Senhas retornadas em respostas da API | CRITICAL | models.py:83-84,98-99 | GET /usuarios expõe todas as senhas sem autenticação |
| 6 | God Methods em models.py — lógica de negócio misturada com acesso a dados | HIGH | models.py:133-169,235-273 | Impossível testar regras de negócio sem banco de dados |
| 7 | Lógica de negócio em controllers.py (validação + notificações fake) | HIGH | controllers.py:28-54,208-210 | Duplicação de validação entre criar e atualizar produto |
| 8 | Problema N+1 na busca de pedidos | MEDIUM | models.py:171-201,203-233 | 3 níveis de queries aninhadas: O(N*M) ao invés de 1 JOIN |
| 9 | Construção de dicts de produto duplicada 3 vezes | MEDIUM | models.py:12-21,31-40,303-313 | Mudanças de schema exigem atualizar 3 locais |
| 10 | Magic numbers nas regras de desconto | LOW | models.py:257-262 | 10000, 5000, 1000, 0.1, 0.05, 0.02 sem constantes nomeadas |

**Total encontrado: 40 findings** (7 CRITICAL, 6 HIGH, 11 MEDIUM, 16 LOW)

---

### Projeto 2 — ecommerce-api-legacy (Node.js/Express LMS API)

| # | Problema | Severidade | Arquivo:Linha | Relevância |
|---|----------|-----------|---------------|-----------|
| 1 | Credenciais de produção hardcoded (gateway de pagamento, DB, SMTP) | CRITICAL | src/utils.js:2-4 | Chave de pagamento live exposta em código-fonte. Comprometimento financeiro direto |
| 2 | Número de cartão de crédito logado no console | CRITICAL | src/AppManager.js:45 | Violação PCI-DSS. Todo sistema de log vira repositório de dados de cartão |
| 3 | Função `badCrypto()` — Base64 não é hash | CRITICAL | src/utils.js:17-23 | Senhas "hasheadas" são trivialmente reversíveis |
| 4 | Endpoint de relatório financeiro admin sem autenticação | CRITICAL | src/AppManager.js:80 | Qualquer pessoa acessa receita de cursos, nomes e pagamentos |
| 5 | God Class AppManager — roteamento + BD + negócio em 139 linhas | HIGH | src/AppManager.js:4-139 | Violação total do SRP. Impossível testar ou escalar |
| 6 | Problema N+1+1 no relatório financeiro | HIGH | src/AppManager.js:83-128 | 4 níveis de callbacks aninhados: O(N*M) queries |
| 7 | Callback hell — 5 níveis de nesting no checkout | HIGH | src/AppManager.js:37-77 | Erros silenciados, controle de fluxo não-determinístico |
| 8 | Dados órfãos ao deletar usuário | HIGH | src/AppManager.js:131-137 | Matrículas e pagamentos ficam sem usuário referenciado (bug admitido no próprio response) |
| 9 | Nomes de variáveis ilegíveis: `u`, `e`, `p`, `cid`, `cc` | MEDIUM | src/AppManager.js:29-33 | Manutenção exige decifrar o código a cada leitura |
| 10 | `cc.startsWith("4")` como lógica de aprovação de pagamento | MEDIUM | src/AppManager.js:46 | Magic string sem documentação. Negócio invisível no código |

**Total encontrado: 31 findings** (4 CRITICAL, 6 HIGH, 9 MEDIUM, 12 LOW)

---

### Projeto 3 — task-manager-api (Python/Flask Task Manager — parcialmente organizado)

| # | Problema | Severidade | Arquivo:Linha | Relevância |
|---|----------|-----------|---------------|-----------|
| 1 | MD5 para hash de senhas — algoritmo quebrado | CRITICAL | models/user.py:28-32 | Rainbow tables crackam MD5 em milissegundos |
| 2 | Hash de senha retornado em todas as respostas de usuário | CRITICAL | models/user.py:21 | Cada GET /users/<id> vaza o hash. 4 endpoints afetados |
| 3 | Credenciais de email hardcoded no código | CRITICAL | services/notification_service.py:9-10 | email_password = 'senha123' comprometido em qualquer leitura do repo |
| 4 | SECRET_KEY hardcoded | CRITICAL | app.py:13 | Mesmo problema do projeto 1 |
| 5 | Lógica de overdue duplicada em 6 lugares — `is_overdue()` nunca chamado | HIGH | task_routes.py:30-38, user_routes.py:170-179, report_routes.py:33-43 | Bug em 1 local exige correção em 6. Método canônico existe mas é ignorado |
| 6 | `validate_status()` e `validate_priority()` nunca chamados — validação duplicada inline | HIGH | task_routes.py:108-112,174-180 | Métodos do model com lógica correta existem mas são bypassados |
| 7 | Category CRUD no arquivo `report_routes.py` | HIGH | report_routes.py:157-223 | Manutenção de categorias não tem relação com relatórios |
| 8 | Sem camada de controllers — toda lógica nas routes | HIGH | routes/*.py | Routes com 50-100 linhas por handler. Lógica não testável sem HTTP |
| 9 | Problema N+1 no GET /tasks | MEDIUM | task_routes.py:40-55 | User.query.get() e Category.query.get() dentro de loop |
| 10 | `datetime.utcnow()` deprecado desde Python 3.12 em 10+ locais | MEDIUM | models/*.py, routes/*.py | Emite DeprecationWarning, quebrará em versões futuras |

**Total encontrado: 38 findings** (4 CRITICAL, 7 HIGH, 10 MEDIUM, 17 LOW)

---

## B) Construção da Skill

### Estrutura da Skill

```
.claude/skills/refactor-arch/
  SKILL.md                  # Prompt principal — instrui o agente nas 3 fases
  project-analysis.md       # Heurísticas de detecção: linguagem, framework, BD, domínio, arquitetura
  anti-patterns-catalog.md  # 10 anti-patterns com sinais de detecção (grep-able) e severidade
  audit-report-template.md  # Template padronizado do relatório (Phase 2)
  mvc-guidelines.md         # Estrutura MVC alvo para Python/Flask e Node.js/Express
  refactoring-playbook.md   # 10 padrões de transformação com before/after code
```

### Decisões de Design

**SKILL.md como prompt de orquestração**: O arquivo principal é intencionalmente um prompt estruturado em fases, com regras explícitas ("NEVER modify files in Phase 2", "ALWAYS pause between Phase 2 and 3"). A instrução de carregar os arquivos de referência antes de qualquer ação garante que o agente tenha todo o conhecimento de domínio antes de analisar o código.

**Catálogo com sinais grep-able**: Cada anti-pattern inclui padrões de regex concretos que o agente pode usar com a ferramenta `Grep`. Por exemplo, para detectar SQL injection: `"execute.*\" +"` e `"execute.*f\""`. Isso é mais acionável do que descrições genéricas como "código ruim".

**Playbook bilíngue**: Cada padrão de transformação inclui exemplos de código antes/depois tanto em Python quanto em Node.js. Isso garante que a refatoração use os idiomas corretos para cada linguagem (werkzeug.security para Python, bcrypt para Node.js).

**Anti-patterns selecionados** (10 no total, cobrindo as 3 stacks):

| # | Anti-pattern | Por que incluir |
|---|-------------|----------------|
| AP-01 | SQL Injection | Presente em 18+ locais no projeto 1 |
| AP-02 | Hardcoded Credentials | Presente nos 3 projetos em variações diferentes |
| AP-03 | Sensitive Data Exposure | Senhas em API, cartão em logs — padrões distintos |
| AP-04 | Arbitrary Code Execution | Endpoint /admin/query exclusivo do projeto 1 |
| AP-05 | God Class/Module | AppManager.js no projeto 2, monolith no projeto 1 |
| AP-06 | Insecure Password Handling | MD5 no projeto 3, badCrypto no projeto 2 |
| AP-07 | N+1 Queries | Presente nos 3 projetos com profundidades diferentes |
| AP-08 | Business Logic in Routes | Padrão universal entre os 3 projetos |
| AP-09 | Dead Code / Unused Modules | `services/` nunca importado no projeto 3 |
| AP-10 | Deprecated API Usage | `datetime.utcnow()` no Python, `new Buffer()` no Node.js |

**Como a skill é agnóstica de tecnologia**:
- `project-analysis.md` mapeia sinais de detecção para múltiplas linguagens e frameworks
- `mvc-guidelines.md` define estruturas alvo separadas para Python/Flask e Node.js/Express, com regras de adaptação para projetos parcialmente organizados
- O `refactoring-playbook.md` fornece exemplos before/after em ambas as linguagens para cada padrão
- A validação na Fase 3 usa comandos condicionais baseados na linguagem detectada na Fase 1

**Desafios encontrados**:
1. **Projeto parcialmente organizado (task-manager-api)**: A skill precisava detectar que o projeto já tinha `models/` e `routes/` e refatorar in-place ao invés de reconstruir do zero. Resolvido adicionando regras de adaptação em `mvc-guidelines.md`.
2. **Validação cross-platform**: A validação via `curl` + processo em background funciona em Unix mas exige atenção no Windows. O SKILL.md especifica os comandos explicitamente para cada runtime.
3. **Callback hell no Node.js**: O código original era impossível de refatorar incrementalmente. A solução foi usar `util.promisify` para converter sqlite3 para async/await, tornando o código linear.

---

## C) Resultados

### Resumo dos Relatórios de Auditoria

| Projeto | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---------|----------|------|--------|-----|-------|
| code-smells-project | 7 | 4 | 5 | 6 | 22 |
| ecommerce-api-legacy | 4 | 4 | 5 | 6 | 19 |
| task-manager-api | 4 | 5 | 5 | 6 | 20 |

### Comparação Antes/Depois

#### Projeto 1 — code-smells-project

**Antes:**
```
code-smells-project/
  app.py          (89 linhas — rotas + admin + config hardcoded)
  controllers.py  (293 linhas — handlers HTTP com validação e notificações)
  models.py       (315 linhas — SQL injection em 18+ pontos, senhas em texto puro)
  database.py     (87 linhas — global mutable state)
```

**Depois:**
```
code-smells-project/
  app.py                         (composition root — create_app factory)
  database.py                    (sem global mutável, schema com FK e NOT NULL)
  src/
    config/settings.py           (todas as configs via env vars)
    models/
      product_model.py           (queries parametrizadas)
      user_model.py              (werkzeug password hash, sem senha na resposta)
      order_model.py             (JOIN ao invés de N+1)
    controllers/
      product_controller.py      (validações e regras de negócio)
      user_controller.py         (login, criação)
      order_controller.py        (criação com validação de estoque)
      report_controller.py       (cálculo de descontos com constantes nomeadas)
    views/
      product_routes.py          (handlers thin — 5-8 linhas por endpoint)
      user_routes.py
      order_routes.py
      report_routes.py
    middlewares/
      error_handler.py           (tratamento centralizado de erros)
```

**Endpoints originais validados**: ✓ GET /produtos, POST /produtos, GET /usuarios, POST /login, POST /pedidos, GET /relatorios/vendas, GET /health

#### Projeto 2 — ecommerce-api-legacy

**Antes:**
```
ecommerce-api-legacy/src/
  app.js          (14 linhas — apenas instancia AppManager)
  AppManager.js   (141 linhas — God Class com tudo)
  utils.js        (25 linhas — credenciais hardcoded, badCrypto)
```

**Depois:**
```
ecommerce-api-legacy/src/
  app.js                              (composition root com async init)
  config/settings.js                  (process.env para todas as configs)
  models/
    db.js                             (sqlite3 promisificado)
    userModel.js                      (bcrypt, cascade delete)
    courseModel.js                    (JOIN para relatório)
    enrollmentModel.js
    auditModel.js
  controllers/
    checkoutController.js             (async/await, sem callback hell)
    reportController.js               (1 query com JOIN ao invés de N*M)
    userController.js
  routes/
    checkoutRoutes.js                 (thin handler)
    reportRoutes.js
    userRoutes.js
  middlewares/
    errorHandler.js
```

**Endpoints originais validados**: ✓ POST /api/checkout, GET /api/admin/financial-report, DELETE /api/users/:id

#### Projeto 3 — task-manager-api

**Antes:**
```
task-manager-api/
  app.py                    (config hardcoded, imports não usados)
  models/user.py            (MD5, senha no to_dict)
  models/task.py            (is_overdue() com bug de indentação, nunca chamado)
  routes/task_routes.py     (300 linhas, overdue duplicado 3x, validate_status ignorado)
  routes/user_routes.py     (212 linhas, regex email duplicado)
  routes/report_routes.py   (224 linhas, Category CRUD misturado com relatórios)
  services/ (dead code)
```

**Depois:**
```
task-manager-api/
  app.py                    (create_app factory, config via env)
  config/settings.py        (todas as configs via os.environ)
  models/user.py            (werkzeug, senha removida do to_dict)
  models/task.py            (is_overdue() corrigido e chamado, validate_status usado)
  models/category.py        (datetime.now(timezone.utc))
  controllers/
    user_controller.py      (toda lógica extraída das routes)
    task_controller.py      (validate_status/priority chamados)
    category_controller.py
    report_controller.py
  routes/
    user_routes.py          (thin — 5-7 linhas por handler)
    task_routes.py          (thin — sem lógica inline)
    report_routes.py        (apenas relatórios, sem category CRUD)
    category_routes.py      (NOVO — category CRUD extraído)
  middlewares/
    error_handler.py
```

**Endpoints originais validados**: ✓ GET /tasks, POST /tasks, GET /users, POST /login, GET /categories, GET /reports/summary, GET /tasks/stats, GET /health

### Checklist de Validação

#### code-smells-project (Projeto 1)
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask 3.1.1)
- [x] Domínio da aplicação descrito corretamente (E-commerce API)
- [x] Número de arquivos analisados condiz com a realidade (4 arquivos)
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade (CRITICAL → LOW)
- [x] Mínimo de 5 findings identificados (22 encontrados)
- [x] Detecção de APIs deprecated incluída (CORS wildcard)
- [x] Skill pausa e pede confirmação antes da Fase 3
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config
- [x] Models criados para abstrair dados (sem SQL injection)
- [x] Views/Routes separadas (Blueprints)
- [x] Controllers concentram o fluxo
- [x] Error handling centralizado
- [x] Entry point claro (create_app factory)
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente (HTTP 200)

#### ecommerce-api-legacy (Projeto 2)
- [x] Linguagem detectada corretamente (JavaScript/Node.js)
- [x] Framework detectado corretamente (Express 4.18.2)
- [x] Domínio da aplicação descrito corretamente (LMS API)
- [x] Número de arquivos analisados condiz com a realidade (3 arquivos)
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] Mínimo de 5 findings identificados (19 encontrados)
- [x] Detecção de APIs deprecated incluída (deprecated callback pattern)
- [x] Skill pausa e pede confirmação antes da Fase 3
- [x] Estrutura de diretórios segue padrão MVC
- [x] Configuração extraída para módulo de config
- [x] God Class decomposta em models/controllers/routes
- [x] Callback hell convertido para async/await
- [x] Error handling centralizado (errorHandler middleware)
- [x] Entry point claro
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

#### task-manager-api (Projeto 3)
- [x] Linguagem detectada corretamente (Python)
- [x] Framework detectado corretamente (Flask + SQLAlchemy)
- [x] Domínio da aplicação descrito corretamente (Task Manager)
- [x] Número de arquivos analisados condiz com a realidade (13 arquivos)
- [x] Relatório segue o template definido
- [x] Cada finding tem arquivo e linhas exatos
- [x] Findings ordenados por severidade
- [x] Mínimo de 5 findings identificados (20 encontrados)
- [x] Detecção de APIs deprecated incluída (datetime.utcnow() em 10+ locais)
- [x] Skill pausa e pede confirmação antes da Fase 3
- [x] Estrutura de diretórios segue padrão MVC (controllers/ adicionado)
- [x] Configuração extraída para módulo de config
- [x] Models existentes mantidos e corrigidos (werkzeug, sem senha no to_dict)
- [x] Controllers criados (lógica extraída das routes)
- [x] Category CRUD movido para category_routes.py
- [x] Error handling centralizado
- [x] Aplicação inicia sem erros
- [x] Endpoints originais respondem corretamente

### Logs de Validação

**Projeto 1 (Python/Flask):**
```
GET /health: 200
GET /produtos: 200
GET /: 200
GET /usuarios: 200
GET /pedidos: 200
GET /relatorios/vendas: 200
```

**Projeto 2 (Node.js/Express):**
```
GET /api/admin/financial-report: 200
POST /api/checkout (valid): 200
DELETE /api/users/99: 200
```

**Projeto 3 (Python/Flask + SQLAlchemy):**
```
GET /health: 200
GET /: 200
GET /tasks: 200
GET /users: 200
GET /categories: 200
GET /reports/summary: 200
GET /tasks/stats: 200
```

---

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) instalado e configurado
- Python 3.11+ (para projetos 1 e 3)
- Node.js 18+ e npm (para projeto 2)

### Setup

```bash
# Clonar o repositório
git clone https://github.com/diovanibmotta/mba-ia-refactor-projects-skill.git
cd mba-ia-refactor-projects-skill
```

### Executar a Skill

```bash
# Projeto 1 — code-smells-project (Python/Flask)
cd code-smells-project
pip install -r requirements.txt
claude "/refactor-arch"

# Projeto 2 — ecommerce-api-legacy (Node.js/Express)
cd ../ecommerce-api-legacy
npm install
claude "/refactor-arch"

# Projeto 3 — task-manager-api (Python/Flask + SQLAlchemy)
cd ../task-manager-api
pip install -r requirements.txt
claude "/refactor-arch"
```

### Validar as Aplicações Refatoradas

```bash
# Projeto 1
cd code-smells-project
python app.py &
curl http://localhost:5000/health
curl http://localhost:5000/produtos
kill %1

# Projeto 2
cd ecommerce-api-legacy
node src/app.js &
curl http://localhost:3000/api/admin/financial-report
curl -X POST http://localhost:3000/api/checkout \
  -H "Content-Type: application/json" \
  -d '{"usr":"Test","eml":"test@test.com","c_id":1,"card":"4111111111111111"}'
kill %1

# Projeto 3
cd task-manager-api
python app.py &
curl http://localhost:5000/health
curl http://localhost:5000/tasks
curl http://localhost:5000/categories
kill %1
```

### Verificar os Relatórios de Auditoria

```bash
cat reports/audit-project-1.md  # E-commerce API — 22 findings
cat reports/audit-project-2.md  # LMS API — 19 findings
cat reports/audit-project-3.md  # Task Manager — 20 findings
```
