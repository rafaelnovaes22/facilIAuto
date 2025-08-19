# Como configurar seu GitHub Personal Access Token

## Passo 1: Criar o Token no GitHub

1. Acesse: https://github.com/settings/tokens
2. Clique em "Generate new token" → "Generate new token (classic)"
3. Dê um nome: "Cursor Upload Token"
4. Selecione as permissões:
   - ✅ repo (todas as opções)
   - ✅ workflow
5. Clique em "Generate token"
6. **COPIE O TOKEN** (só aparece uma vez!)

## Passo 2: Usar o Token para Push

Execute este comando substituindo os valores:

```bash
cd /workspace/feira-bras-app

# Substitua SEU_USUARIO e SEU_TOKEN pelos valores reais
git remote set-url origin https://SEU_USUARIO:SEU_TOKEN@github.com/rafaelnovaes22/modexar.git

# Agora faça o push
git push -u origin main
```

### Exemplo:
```bash
# Se seu usuário é "rafaelnovaes22" e token é "ghp_abc123..."
git remote set-url origin https://rafaelnovaes22:ghp_abc123...@github.com/rafaelnovaes22/modexar.git
git push -u origin main
```

## Alternativa: Usar GitHub CLI

```bash
# Instalar GitHub CLI (se não tiver)
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Autenticar
gh auth login

# Fazer push
gh repo create rafaelnovaes22/modexar --source=. --push --public
```

## ⚠️ Segurança

- **NUNCA** compartilhe seu token
- Tokens expiram (configure a expiração)
- Após o push, remova o token do remote:
  ```bash
  git remote set-url origin https://github.com/rafaelnovaes22/modexar.git
  ```