#!/bin/bash
set -e

# PostgreSQL initialization script for all microservices
# This script creates all databases and users needed by the hospitality platform

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    -- Auth Service
    CREATE DATABASE auth_db;
    CREATE USER auth_user WITH PASSWORD 'auth_password';
    GRANT ALL PRIVILEGES ON DATABASE auth_db TO auth_user;

    -- Guest Interaction Service
    CREATE DATABASE guest_interaction_db;
    CREATE USER guest_user WITH PASSWORD 'guest_password';
    GRANT ALL PRIVILEGES ON DATABASE guest_interaction_db TO guest_user;

    -- Booking Reservation Service
    CREATE DATABASE booking_reservation_db;
    CREATE USER booking_user WITH PASSWORD 'booking_password';
    GRANT ALL PRIVILEGES ON DATABASE booking_reservation_db TO booking_user;

    -- Dynamic Pricing Service
    CREATE DATABASE dynamic_pricing_db;
    CREATE USER pricing_user WITH PASSWORD 'pricing_password';
    GRANT ALL PRIVILEGES ON DATABASE dynamic_pricing_db TO pricing_user;

    -- Payment Billing Service
    CREATE DATABASE payment_billing_db;
    CREATE USER payment_user WITH PASSWORD 'payment_password';
    GRANT ALL PRIVILEGES ON DATABASE payment_billing_db TO payment_user;

    -- Inventory Resource Service
    CREATE DATABASE inventory_db;
    CREATE USER inventory_user WITH PASSWORD 'inventory_password';
    GRANT ALL PRIVILEGES ON DATABASE inventory_db TO inventory_user;

    -- Feedback Sentiment Service
    CREATE DATABASE feedback_sentiment_db;
    CREATE USER feedback_user WITH PASSWORD 'feedback_password';
    GRANT ALL PRIVILEGES ON DATABASE feedback_sentiment_db TO feedback_user;

    -- Marketing Loyalty Service
    CREATE DATABASE marketing_loyalty_db;
    CREATE USER marketing_user WITH PASSWORD 'marketing_password';
    GRANT ALL PRIVILEGES ON DATABASE marketing_loyalty_db TO marketing_user;

    -- BI Analytics Service
    CREATE DATABASE bi_analytics_db;
    CREATE USER analytics_user WITH PASSWORD 'analytics_password';
    GRANT ALL PRIVILEGES ON DATABASE bi_analytics_db TO analytics_user;

    -- Housekeeping Maintenance Service
    CREATE DATABASE housekeeping_db;
    CREATE USER housekeeping_user WITH PASSWORD 'housekeeping_password';
    GRANT ALL PRIVILEGES ON DATABASE housekeeping_db TO housekeeping_user;

    -- Favorites Collections Service
    CREATE DATABASE favorites_collections_db;
    CREATE USER favorites_user WITH PASSWORD 'favorites_password';
    GRANT ALL PRIVILEGES ON DATABASE favorites_collections_db TO favorites_user;
EOSQL

# Grant schema privileges for each database
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "auth_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO auth_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO auth_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO auth_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "guest_interaction_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO guest_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO guest_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO guest_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "booking_reservation_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO booking_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO booking_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO booking_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "dynamic_pricing_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO pricing_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO pricing_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO pricing_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "payment_billing_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO payment_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO payment_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO payment_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "inventory_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO inventory_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO inventory_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO inventory_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "feedback_sentiment_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO feedback_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO feedback_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO feedback_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "marketing_loyalty_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO marketing_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO marketing_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO marketing_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "bi_analytics_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO analytics_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO analytics_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO analytics_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "housekeeping_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO housekeeping_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO housekeeping_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO housekeeping_user;
EOSQL

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "favorites_collections_db" <<-EOSQL
    GRANT ALL ON SCHEMA public TO favorites_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO favorites_user;
    ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO favorites_user;
EOSQL

