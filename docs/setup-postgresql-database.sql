-- PostgreSQL Database Setup Script for Casino Management System
-- Run this as PostgreSQL superuser (usually 'postgres')

-- Create database
CREATE DATABASE casino_db
    WITH 
    OWNER = postgres
    ENCODING = 'UTF8'
    LC_COLLATE = 'en_US.UTF-8'
    LC_CTYPE = 'en_US.UTF-8'
    TABLESPACE = pg_default
    CONNECTION LIMIT = -1;

-- Create user for the casino application
CREATE USER casino_user WITH
    LOGIN
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    INHERIT
    NOREPLICATION
    CONNECTION LIMIT -1
    PASSWORD 'your_secure_password_here';

-- Grant privileges to the user
GRANT CONNECT ON DATABASE casino_db TO casino_user;
GRANT USAGE ON SCHEMA public TO casino_user;
GRANT CREATE ON SCHEMA public TO casino_user;

-- Connect to the casino_db database to set up table permissions
\c casino_db

-- Grant all privileges on all tables in public schema
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO casino_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO casino_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO casino_user;

-- Grant default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO casino_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO casino_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON FUNCTIONS TO casino_user;

-- Optional: Create a schema specifically for the casino application
-- CREATE SCHEMA IF NOT EXISTS casino_app AUTHORIZATION casino_user;

COMMENT ON DATABASE casino_db IS 'Casino Management System Database';
COMMENT ON ROLE casino_user IS 'Application user for Casino Management System'; 