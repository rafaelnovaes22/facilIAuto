-- 🗄️ Script de Inicialização do Banco - FacilIAuto
-- Configurações básicas para PostgreSQL em container

-- Configurar encoding
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- Para fuzzy matching
CREATE EXTENSION IF NOT EXISTS "unaccent"; -- Para remoção de acentos

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Log de inicialização
DO $$
BEGIN
    RAISE NOTICE 'FacilIAuto Database initialized successfully!';
    RAISE NOTICE 'Extensions: uuid-ossp, pg_trgm, unaccent';
    RAISE NOTICE 'Timezone: America/Sao_Paulo';
    RAISE NOTICE 'Encoding: UTF8';
END
$$;
