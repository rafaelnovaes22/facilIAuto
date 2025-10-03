# 🤖 Framework de Agentes Especializados

## 📋 **Visão Geral**

Framework com **12 agentes especializados** que fornecem contexto e expertise em diferentes áreas do desenvolvimento do FacilIAuto.

---

## 🎯 **Agentes Disponíveis**

### **Agentes Core (Técnicos)**
- **ai-engineer/** - IA responsável e guardrails
- **tech-lead/** - Liderança técnica e arquitetura
- **ux-especialist/** - Experiência do usuário B2B
- **system-architecture/** - Governança técnica

### **Agentes Business**
- **business-analyst/** - Análise de negócios
- **product-manager/** - Visão e estratégia de produto
- **marketing-strategist/** - Growth e branding
- **financial-advisor/** - Estratégia financeira
- **sales-coach/** - Performance de vendas

### **Agentes Operations**
- **operations-manager/** - Processos e eficiência
- **data-analyst/** - Insights e analytics
- **content-creator/** - UX/UI e storytelling

---

## 🛠️ **Ferramentas CLI**

### **agent-cli.py**
CLI para gerenciar agentes:
```bash
python agent-cli.py list        # Listar todos os agentes
python agent-cli.py validate    # Validar contextos
python agent-cli.py create      # Criar novo agente
```

### **orchestrator.py**
Sistema de orquestração de agentes para decisões colaborativas.

### **orchestrated_cli.py**
Interface CLI orquestrada.

### **run_orchestrator.py**
Script de execução do orchestrator.

---

## 📁 **Estrutura de Cada Agente**

```
agent-name/
└── context.md          # Contexto, expertise e guidelines
```

---

## 📚 **Documentação**

Cada agente possui um arquivo `context.md` com:
- 🎯 Propósito e responsabilidades
- 💡 Expertise e conhecimento
- 📋 Guidelines e best practices
- 🔗 Relações com outros agentes

---

**Total:** 12 agentes + 4 ferramentas de orquestração

