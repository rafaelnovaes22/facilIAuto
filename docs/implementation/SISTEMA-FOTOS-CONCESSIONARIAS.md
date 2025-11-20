# 📸 Sistema de Fotos dos Carros das Concessionárias - Plano de Implementação

**Objetivo:** Permitir que concessionárias façam upload e gerenciamento das fotos de seus veículos diretamente pela plataforma.

## 📋 Tarefas

### 1. Backend (FastAPI)

- [x] **Criar Endpoint de Upload**
  - `POST /api/dealerships/{dealership_id}/cars/{car_id}/images`
  - Aceitar upload de múltiplos arquivos (multipart/form-data)
  - Validar tipo de arquivo (jpg, png, webp) e tamanho (< 5MB)
  - Salvar arquivos em diretório local `platform/backend/data/images/{dealership_id}/{car_id}/` (MVP) ou S3 (Produção)
  - Atualizar lista de `imagens` no objeto `Car`

- [ ] **Criar Endpoint de Remoção**
  - `DELETE /api/dealerships/{dealership_id}/cars/{car_id}/images/{image_filename}`
  - Remover arquivo do disco
  - Atualizar lista de `imagens` no objeto `Car`

- [ ] **Criar Endpoint de Reordenação** (Opcional MVP)
  - `PUT /api/dealerships/{dealership_id}/cars/{car_id}/images/order`
  - Receber nova lista de URLs/nomes

### 2. Frontend (React)

- [x] **Criar Componente `PhotoUpload`**
  - Área de Drag & Drop
  - Preview das imagens selecionadas
  - Barra de progresso de upload
  - Tratamento de erros

- [x] **Criar Componente `PhotoGalleryManager`**
  - Visualizar fotos atuais do carro
  - Botão de excluir para cada foto
  - (Opcional) Drag & drop para reordenar

- [x] **Integrar no Dashboard da Concessionária**
  - Adicionar aba "Fotos" na edição do veículo
  - Conectar com API de upload e delete

### 3. Infraestrutura / Armazenamento

- [x] **Configurar Diretório de Imagens**
  - Garantir que `platform/backend/data/images` exista e tenha permissões
  - Configurar `StaticFiles` no FastAPI para servir essas imagens em `/static/images`

## 🚀 Execução

Para iniciar a execução, confirme qual etapa deseja priorizar.
