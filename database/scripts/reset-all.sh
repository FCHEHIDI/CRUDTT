#!/bin/bash
# Toujours s'exécuter depuis le répertoire database/ (parent de scripts/)
cd "$(dirname "$0")/.." || exit 1

echo "🔄 Resetting all database data..."

read -p "⚠️  This will destroy ALL data in both databases. Continue? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🛑 Stopping all containers and removing project volumes..."
    docker compose --profile all down -v

    echo "✅ All data reset completed!"
    echo "💡 Use './scripts/start-mysql.sh' or './scripts/start-postgres.sh' to restart"
else
    echo "❌ Reset cancelled"
fi
