-- PostGIS initialization SQL
-- Runs automatically when the Docker container starts for the first time

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS pg_trgm;  -- for fuzzy text search on water body names

-- Enable btree_gist for combined spatial+attribute indexes
CREATE EXTENSION IF NOT EXISTS btree_gist;

