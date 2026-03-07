#!/bin/bash
# Toujours s'exécuter depuis le répertoire database/ (parent de scripts/)
cd "$(dirname "$0")/.." || exit 1

echo "🐬 Starting MySQL Stack (MySQL + phpMyAdmin)..."
docker compose --profile mysql up -d

echo "⏳ Waiting for services to be healthy..."
sleep 10

echo "✅ MySQL Stack Ready!"
echo ""
echo "🔗 Access Information:"
echo "   MySQL: localhost:${MYSQL_PORT:-3306}"
echo "   phpMyAdmin: http://localhost:${PHPMYADMIN_PORT:-8080}"
echo "   Database: ${MYSQL_DATABASE:-internal_tools}"
echo "   User: ${MYSQL_USER:-dev}"
echo ""
echo "📊 Connection String:"
echo "   mysql://${MYSQL_USER:-dev}:${MYSQL_PASSWORD:-dev123}@localhost:${MYSQL_PORT:-3306}/${MYSQL_DATABASE:-internal_tools}"
