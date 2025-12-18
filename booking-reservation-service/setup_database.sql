-- Database setup script for Booking & Reservation Service
-- Run this script as PostgreSQL superuser (usually 'postgres')

-- Create database
CREATE DATABASE booking_reservation_db;

-- Create user
CREATE USER booking_user WITH PASSWORD 'booking_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON DATABASE booking_reservation_db TO booking_user;

-- Connect to the database and grant schema privileges
\c booking_reservation_db
GRANT ALL ON SCHEMA public TO booking_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO booking_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO booking_user;

