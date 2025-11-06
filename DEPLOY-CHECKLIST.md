# ✅ Checklist Rápido: Deploy Railway

**Tempo**: 20-30 minutos

---

## 🚂 Backend (10 min)

- [ ] 1. Acessar https://railway.app e fazer login com GitHub
- [ ] 2. Criar "New Project" → "Deploy from GitHub repo"
- [ ] 3. Selecionar repositório `rafaelnovaes22/facilIAuto`
- [ ] 4. Configurar serviço:
  - Nome: `faciliauto-backend`
  - Root Directory: `platform/backend`
- [ ] 5. Adicionar variáveis de ambiente:
  ```
  PORT=8000
  PYTHONUNBUFFERED=1
  ENVIRONMENT=production
  LOG_LEVEL=info
  ```
- [ ] 6. Settings → Networking → "Generate Domain"
- [ ] 7. **COPIAR URL DO BACKEND**: _______________________________
- [ ] 8. Testar: `https://[backend-url]/health`
- [ ] 9. Testar: `https://[backend-url]/docs`

---

## 🎨 Frontend (10 min)

- [ ] 10. No mesmo projeto, clicar "+ New" → "GitHub Repo"
- [ ] 11. Selecionar `facilIAuto` novamente
- [ ] 12. Configurar serviço:
  - Nome: `faciliauto-frontend`
  - Root Directory: `platform/frontend`
- [ ] 13. Adicionar variáveis de ambiente:
  ```
  PORT=3000
  NODE_ENV=production
  VITE_API_URL=https://[COLAR-URL-BACKEND-AQUI]
  ```
- [ ] 14. Settings → Networking → "Generate Domain"
- [ ] 15. **COPIAR URL DO FRONTEND**: _______________________________
- [ ] 16. Voltar ao Backend → Variables → Adicionar:
  ```
  FRONTEND_URL=https://[COLAR-URL-FRONTEND-AQUI]
  ```
- [ ] 17. Backend → "Redeploy"
- [ ] 18. Aguardar deploy do frontend (2-3 min)

---

## ✅ Validação (5 min)

- [ ] 19. Acessar frontend: `https://[frontend-url]`
- [ ] 20. Página inicial carrega?
- [ ] 21. Preencher questionário completo
- [ ] 22. Ver recomendações?
- [ ] 23. TCO e badges aparecem?
- [ ] 24. Expandir detalhes do TCO funciona?

---

## 🎉 Pronto!

**Backend**: https://________________________________

**Frontend**: https://________________________________

**API Docs**: https://________________________________/docs

---

## 🆘 Problemas?

Veja: `DEPLOY-RAILWAY-GUIA-COMPLETO.md`
