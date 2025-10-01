# 📊 Requisitos Detalhados para Frontend - Sistema de Vendas e Previsões ML

## 🎯 Visão Geral do Projeto

Sistema web completo para gestão de vendas com análise de dados e previsões de Machine Learning para joalherias. O frontend deve ser uma aplicação moderna, responsiva e intuitiva que integra com uma API FastAPI existente.

## 🛠️ Tecnologias Obrigatórias

### Frontend Principal
- **Framework**: React.js (versão 18+) com TypeScript
- **Estilização**: Tailwind CSS + Headless UI ou Material-UI (MUI)
- **Gráficos**: Chart.js ou Recharts para visualizações
- **Estado**: Context API + useState/useReducer ou Redux Toolkit
- **Roteamento**: React Router v6+
- **HTTP Client**: Axios ou Fetch API
- **Autenticação**: JWT tokens com localStorage/sessionStorage

### Estrutura de Pastas Recomendada
```
src/
├── components/
│   ├── auth/
│   ├── charts/
│   ├── dashboard/
│   ├── forms/
│   └── common/
├── pages/
├── hooks/
├── services/
├── types/
├── utils/
└── contexts/
```

## 🔐 Sistema de Autenticação

### Tela de Login/Registro
**Endpoint de integração**: `POST /auth/login` e `POST /auth/register`

#### Funcionalidades Obrigatórias:
- **Layout em Abas**: Login e Cadastro em tabs separadas
- **Campos de Login**:
  - Email (validação de formato)
  - Senha (campo password com toggle de visibilidade)
  - Botão "Entrar" (primary style)
- **Campos de Cadastro**:
  - Email (validação única)
  - Senha (mín. 4 caracteres)
  - Confirmar senha (validação de igualdade)
  - Botão "Cadastrar"
- **Credenciais Padrão**: Exibir box info com admin@admin.com / admin
- **Estados de Loading**: Spinners durante requisições
- **Tratamento de Erros**: Toasts/alerts para erros de validação e servidor

#### Especificações Técnicas:
```typescript
interface LoginForm {
  email: string;
  password: string;
}

interface RegisterForm {
  email: string;
  password: string;
  confirmPassword: string;
}

// Headers para requests autenticados
const authHeaders = {
  'Authorization': `Bearer ${token}`
}
```

## 📊 Dashboard Principal

### Layout e Estrutura
- **Header**: Logo, título, botões de ação (ML, Refresh, Logout)
- **Sidebar/Menu**: Navegação entre Dashboard, Import, Configurações
- **Layout Responsivo**: Grid flexível que se adapta a diferentes telas
- **Auto-refresh**: Opção de atualização automática dos dados

### KPIs Principais (Cards de Métricas)
**Endpoint**: `GET /metrics`

#### Cards Obrigatórios:
1. **Receita Total**
   - Valor formatado em R$ (padrão brasileiro: 1.234,56)
   - Delta de crescimento mensal (% com cor verde/vermelho)
   - Ícone: 💰

2. **Ticket Médio**
   - Valor em R$ formatado
   - Variação percentual
   - Ícone: 🎯

3. **Total de Vendas**
   - Número de vendas (formato: 1.234)
   - Progresso da meta (barra ou %)
   - Ícone: 🛒

4. **Produtos Únicos**
   - Quantidade de produtos diferentes
   - Produto destaque (nome truncado)
   - Ícone: 📦

### Gráficos Principais

#### 1. Evolução da Receita Mensal
- **Tipo**: Gráfico de linha com marcadores
- **Dados**: `metrics.evolucao_mensal`
- **Eixo X**: Mês (formato MM/YYYY)
- **Eixo Y**: Receita (R$)
- **Features**: Hover com detalhes, responsivo

#### 2. Previsões ML
**Endpoint**: `GET /forecast`
- **Tipo**: Gráfico de barras ou combinado (linha histórica + barras previstas)
- **Dados**: Agregação de `qtd_prevista` por `data_prevista`
- **Diferenciação visual**: Cores diferentes para histórico vs previsão
- **Tooltip**: Valores formatados em R$

## 🤖 Sistema de Machine Learning

### Botão Executar ML
**Endpoint**: `POST /run-ml`

#### Funcionalidades:
- **Loading State**: Spinner com texto "Executando ML..."
- **Timeout**: 60 segundos máximo
- **Feedback Visual**: 
  - Sucesso: Toast verde + recarregamento automático
  - Erro: Toast vermelho com detalhes
- **Estados**: Disabled durante execução
- **Posicionamento**: Header principal + abas onde necessário

### Exibição de Previsões

#### Produto Destaque
- **Cálculo**: Maior `qtd_prevista` total por produto
- **Exibição**: Nome do produto + valor previsto
- **Fallback**: "ID {produto_id}" se `produto_nome` não disponível

#### Top 3 Produtos Previstos
- Lista numerada (1º, 2º, 3º)
- Nome + receita prevista formatada
- Atualização automática após ML

## 📈 Sistema de Abas Detalhadas

### Aba 1: Vendas por Categoria
**Dados**: `metrics.vendas_categoria`

#### Layout em 2 Colunas:
1. **Gráfico de Pizza**:
   - Categorias como labels
   - Receitas como values
   - Percentuais visíveis
   - Cores distintas

2. **Tabela Detalhada**:
   - Colunas: Categoria, Receita, Qtd Vendas, Participação %
   - Ordenação por receita (desc)
   - Formatação monetária

### Aba 2: Análise de Tendências

#### Gráfico de Área
- **Dados**: `metrics.evolucao_mensal`
- **Estilo**: Área preenchida com gradiente
- **Features**: Zoom, pan, responsivo

#### Métricas de Crescimento
- **Crescimento Total**: Cálculo de % entre primeiro e último mês
- **Média Mensal**: Média aritmética das receitas
- **Melhor Mês**: Maior valor registrado

#### Projeção Simples
- **Algoritmo**: Taxa de crescimento médio aplicada aos próximos 3 meses
- **Exibição**: 3 cards com "Mês +1", "Mês +2", "Mês +3"

### Aba 3: Previsões ML Detalhadas

#### Gráfico Combinado Histórico + Previsão
- **Linha Histórica**: Dados de `metrics.evolucao_mensal`
- **Linha de Previsão**: Dados de forecast agregados
- **Estilos**: Linha sólida (histórico) + tracejada (previsão)
- **Cores**: Verde (histórico) + dourado (previsão)

#### Ranking de Produtos
- **Gráfico de Barras**: Top 10 produtos por receita prevista
- **Dados**: Agregação de `qtd_prevista` por `produto_nome`/`produto_id`
- **Ordenação**: Descendente por receita
- **Labels**: Nomes dos produtos (ou ID como fallback)

#### Tabelas Detalhadas (2 colunas):
1. **Receita Mensal Prevista**:
   - Colunas: Mês, Receita Prevista
   - Formato de data: MM/YYYY

2. **Top Produtos Detalhado**:
   - Colunas: Produto, Receita Prevista, Nº Previsões
   - Top 5 produtos

#### Estatísticas ML (4 cards):
- Receita Total Prevista
- Receita Média Mensal
- Produto Top
- Produtos Ativos

### Aba 4: Top Produtos
**Dados**: `metrics.top_produtos`

#### Gráficos:
1. **Barras Horizontais**: Produtos por receita
2. **Barras Verticais**: Produtos por quantidade
3. **Tabela Completa**: Produto, Receita Total, Qtd Vendida

### Aba 5: Dados Técnicos
- **JSON Viewers**: Expandable para métricas e forecast
- **Info do Sistema**: URL da API, total de endpoints, última sincronização
- **Debug**: Logs de requisições (opcional)

## 📂 Importação de Dados

### Página de Upload CSV
**Endpoint**: `POST /import`

#### Funcionalidades Obrigatórias:
- **File Upload**: Drag & drop + botão de seleção
- **Validação**: Apenas arquivos .csv
- **Preview**: Tabela dos primeiros registros
- **Formato Esperado**: Documentação clara do CSV
- **Feedback**: Loading + success/error states
- **Headers**: Authorization com JWT token

#### Exemplo de CSV:
```csv
data,produto,categoria,preco,quantidade,valor_total
2025-01-01,Anel Ouro 18K,Anéis,3500.00,1,3500.00
```

## 🎨 Design System e UX

### Paleta de Cores
- **Primária**: Verde (#2E8B57) para sucesso e crescimento
- **Secundária**: Dourado (#FFD700) para previsões ML
- **Neutros**: Cinzas para backgrounds e textos
- **Estados**: Verde (sucesso), Vermelho (erro), Azul (info)

### Tipografia
- **Título Principal**: Font-size 2xl-3xl, font-weight bold
- **Subtítulos**: Font-size lg-xl, font-weight semibold
- **Corpo**: Font-size base, font-weight normal
- **Métricas**: Font-size xl-2xl, font-weight bold

### Componentes Visuais

#### Cards de Métricas
- **Estilo**: Background gradiente escuro, bordas arredondadas
- **Shadow**: Box-shadow sutil
- **Hover**: Elevação e mudança de borda
- **Ícones**: Emojis ou ícones SVG consistentes

#### Botões
- **Primary**: Background verde, texto branco
- **Secondary**: Outline verde, texto verde
- **States**: Hover, focus, disabled, loading

#### Gráficos
- **Tema**: Fundo transparente
- **Cores**: Paleta consistente
- **Animations**: Transições suaves
- **Responsive**: Adaptável a diferentes tamanhos

## 🔧 Aspectos Técnicos

### Formatação de Números
```typescript
// Padrão brasileiro
const formatBrazilianCurrency = (value: number): string => {
  return new Intl.NumberFormat('pt-BR', {
    style: 'currency',
    currency: 'BRL'
  }).format(value);
};

const formatNumber = (value: number, decimals: number = 2): string => {
  return value.toLocaleString('pt-BR', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};
```

### Tratamento de Datas
```typescript
const formatDate = (date: string): string => {
  return new Date(date).toLocaleDateString('pt-BR');
};

const formatMonth = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('pt-BR', {
    year: 'numeric',
    month: '2-digit'
  });
};
```

### Gerenciamento de Estado
```typescript
interface AppState {
  user: User | null;
  token: string | null;
  metrics: MetricsData | null;
  forecasts: ForecastData[];
  loading: {
    auth: boolean;
    metrics: boolean;
    forecast: boolean;
    ml: boolean;
  };
  errors: {
    [key: string]: string | null;
  };
}
```

### Tipos TypeScript Obrigatórios
```typescript
interface MetricsData {
  receita_total: number;
  ticket_medio: number;
  produto_mais_vendido: string | null;
  evolucao_mensal: Array<{
    mes: string;
    receita: number;
  }>;
  top_produtos: Array<{
    nome: string;
    receita: number;
    quantidade: number;
  }>;
  vendas_categoria: Array<{
    categoria: string;
    receita: number;
    num_vendas: number;
  }>;
  total_vendas: number;
  produtos_unicos: number;
}

interface ForecastData {
  produto_id: number;
  produto_nome?: string;
  data_prevista: string;
  qtd_prevista: number;
  intervalo_conf: string;
}

interface User {
  email: string;
}
```

## 🚨 Alertas e Insights

### Sistema de Notificações
- **Toast/Snackbar**: Para feedback de ações
- **Alerts**: Para insights importantes
- **Status Cards**: Para métricas em tempo real

### Insights Automáticos
1. **Meta de Receita**: Comparação com valor pré-definido (R$ 50.000)
2. **Status ML**: Indicador se previsões estão atualizadas
3. **Crescimento**: Alert sobre tendências positivas/negativas
4. **Recomendações**: Sugestões baseadas nos dados

## 📱 Responsividade

### Breakpoints
- **Mobile**: < 768px (layout em coluna única)
- **Tablet**: 768px - 1024px (layout adaptado)
- **Desktop**: > 1024px (layout completo)

### Adaptações Mobile
- **Sidebar**: Drawer colapsável
- **Gráficos**: Altura reduzida, scroll horizontal se necessário
- **Tabelas**: Scroll horizontal
- **Cards**: Stack vertical

## ⚡ Performance e Otimização

### Lazy Loading
- **Componentes**: React.lazy para páginas
- **Gráficos**: Carregamento sob demanda
- **Dados**: Paginação quando aplicável

### Cache
- **Dados**: Cache de métricas por alguns minutos
- **Imagens**: Lazy loading de assets
- **API**: Invalidação inteligente de cache

## 🧪 Testes (Opcional mas Recomendado)

### Testes Unitários
- **React Testing Library**: Para componentes
- **Jest**: Para funções utilitárias
- **Mock Service Worker**: Para APIs

### Casos de Teste Críticos
1. Fluxo de login/logout
2. Upload de CSV
3. Execução de ML
4. Formatação de números/datas
5. Responsividade

## 📦 Build e Deploy

### Scripts Package.json
```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "jest"
  }
}
```

### Variáveis de Ambiente
```env
VITE_API_URL=http://localhost:8001
VITE_APP_TITLE=Sistema de Vendas & ML
```

## 🔗 Integração com Backend

### Base URL da API
- **Desenvolvimento**: http://localhost:8001
- **Headers Padrão**: Content-Type: application/json
- **Autenticação**: Bearer token em Authorization header

### Endpoints Utilizados
1. `POST /auth/login` - Login
2. `POST /auth/register` - Cadastro
3. `GET /metrics` - Métricas principais
4. `GET /forecast` - Previsões ML
5. `POST /run-ml` - Executar ML
6. `POST /import` - Upload CSV

### Tratamento de Erros HTTP
- **401**: Redirect para login
- **403**: Mensagem de permissão negada
- **404**: Recurso não encontrado
- **500**: Erro interno do servidor
- **Network Error**: Verificar conectividade

## 📋 Checklist de Implementação

### ✅ Autenticação
- [ ] Tela de login/registro
- [ ] Gerenciamento de JWT tokens
- [ ] Proteção de rotas
- [ ] Logout funcional

### ✅ Dashboard
- [ ] Layout responsivo
- [ ] 4 cards de KPIs principais
- [ ] Gráfico de evolução mensal
- [ ] Gráfico de previsões ML
- [ ] Sistema de abas detalhadas

### ✅ Machine Learning
- [ ] Botão executar ML
- [ ] Loading states
- [ ] Feedback visual
- [ ] Atualização automática pós-ML

### ✅ Importação
- [ ] Upload de CSV
- [ ] Preview dos dados
- [ ] Validação de formato
- [ ] Feedback de sucesso/erro

### ✅ Visualizações
- [ ] Gráficos responsivos
- [ ] Formatação brasileira de números
- [ ] Cores consistentes
- [ ] Animações suaves

### ✅ UX/UI
- [ ] Design system implementado
- [ ] Componentização adequada
- [ ] Estados de loading
- [ ] Tratamento de erros
- [ ] Responsividade completa

---

**🎯 Objetivo Final**: Criar um dashboard moderno, intuitivo e funcional que permita gestão completa de vendas com insights de ML, priorizando experiência do usuário e qualidade técnica.