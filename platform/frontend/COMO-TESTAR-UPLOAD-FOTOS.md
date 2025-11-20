# 📸 Como Testar o Sistema de Upload de Fotos

## 1. Preparação

Certifique-se de que o backend e o frontend estejam rodando.

### Backend
```bash
cd platform/backend
python api/main.py
```

### Frontend
```bash
cd platform/frontend
npm run dev
```

## 2. Acessar a Página de Gestão

1. Abra o navegador em `http://localhost:3000/admin/inventory`
2. Você verá a página "Gestão de Estoque - Fotos"

## 3. Testar Upload

1. **Selecionar Veículo**: No dropdown, selecione um veículo (ex: "FIAT CRONOS DRIVE 1.3").
2. **Verificar Galeria**: A aba "Galeria Atual" deve mostrar as fotos existentes (se houver).
3. **Upload**:
   - Clique na aba "Upload de Fotos".
   - Arraste e solte algumas imagens (JPG, PNG) na área pontilhada OU clique para selecionar arquivos.
   - Você verá uma prévia das imagens.
   - Clique em "Enviar Todas".
   - As barras de progresso devem encher e mostrar "Sucesso".
4. **Verificar Resultado**:
   - Volte para a aba "Galeria Atual".
   - As novas fotos devem aparecer lá.
   - Passe o mouse sobre uma foto para ver os botões de "Excluir" e "Definir como Principal".

## 4. Verificar Backend

1. Verifique se a pasta `platform/backend/data/images/robustcar/{car_id}/` foi criada.
2. Verifique se os arquivos de imagem estão lá.

## 5. Testar Erros (Opcional)

1. Tente fazer upload de um arquivo de texto (.txt). O sistema deve rejeitar.
2. Tente fazer upload com o backend desligado. O sistema deve mostrar erro.
