-- ──────────────────────────────────────────────
-- Velour — PostgreSQL initialization script
-- Enables required extensions only.
-- Tables are managed by Alembic migrations.
-- ──────────────────────────────────────────────

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enable cryptographic functions
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
