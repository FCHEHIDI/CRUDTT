#!/bin/bash
# Toujours s'exécuter depuis le répertoire database/ (parent de scripts/)
cd "$(dirname "$0")/.." || exit 1

echo "🐘 Starting PostgreSQL Stack (PostgreSQL + pgAdmin)..."
docker compose --profile postgres up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo "✅ PostgreSQL Stack Ready!"
echo ""
echo "🔗 Access Information:"
echo "   PostgreSQL: localhost:${POSTGRES_PORT:-5432}"
echo "   pgAdmin: http://localhost:${PGADMIN_PORT:-8081}"
echo "   Database: ${POSTGRES_DATABASE:-internal_tools}"
echo "   User: ${POSTGRES_USER:-dev}"
echo ""
echo "📊 Connection String:"
echo "   postgresql://${POSTGRES_USER:-dev}:${POSTGRES_PASSWORD:-dev123}@localhost:${POSTGRES_PORT:-5432}/${POSTGRES_DATABASE:-internal_tools}"
