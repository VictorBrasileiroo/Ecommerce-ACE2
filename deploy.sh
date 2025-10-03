#!/bin/bash
# Script de deploy automatizado para Render

echo "🚀 Preparando deploy do ACE2..."

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Execute este script no diretório raiz do projeto"
    exit 1
fi

# Verificar se o git está inicializado
if [ ! -d ".git" ]; then
    echo "📦 Inicializando repositório Git..."
    git init
fi

# Adicionar todos os arquivos
echo "📁 Adicionando arquivos..."
git add .

# Fazer commit
echo "💾 Fazendo commit..."
git commit -m "Deploy: ACE2 Sistema de Vendas e ML - $(date +%Y%m%d%H%M%S)"

# Verificar se origin já existe
if git remote get-url origin > /dev/null 2>&1; then
    echo "📡 Fazendo push para origin existente..."
    git push
else
    echo "❗ Configure o remote origin primeiro:"
    echo "   git remote add origin https://github.com/VictorBrasileiroo/SEU_REPOSITORIO.git"
    echo "   git push -u origin main"
fi

echo "✅ Código preparado para deploy!"
echo ""
echo "🔗 Próximos passos:"
echo "1. Acesse render.com"
echo "2. Conecte seu repositório GitHub"
echo "3. Crie 2 Web Services (backend e frontend)"
echo "4. Use as configurações do arquivo DEPLOY_RENDER.md"