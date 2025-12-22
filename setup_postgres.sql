-- Script de configuración inicial de PostgreSQL para VerificarSms
-- Fecha: 22 de diciembre de 2025

-- Crear base de datos
CREATE DATABASE verificarsms
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'Spanish_Argentina.1252'
    LC_CTYPE = 'Spanish_Argentina.1252'
    TEMPLATE = template0;

-- Crear usuario
CREATE USER verificarsms_user WITH PASSWORD 'VerificarSMS2025!';

-- Dar permisos completos sobre la base de datos
GRANT ALL PRIVILEGES ON DATABASE verificarsms TO verificarsms_user;

-- Cambiar el owner de la base de datos
ALTER DATABASE verificarsms OWNER TO verificarsms_user;

-- Conectar a la base de datos para dar permisos adicionales
\c verificarsms

-- Dar permisos en el schema public
GRANT ALL ON SCHEMA public TO verificarsms_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO verificarsms_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO verificarsms_user;

-- Configurar permisos por defecto para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO verificarsms_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO verificarsms_user;

-- Verificar que todo se creó correctamente
SELECT 'Base de datos verificarsms creada y configurada exitosamente' AS mensaje;
