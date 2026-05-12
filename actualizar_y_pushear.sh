#!/bin/bash
# Actualiza el hub con los últimos reportes y pushea a GitHub (Netlify auto-deploya)
cd "$(dirname "$0")"

echo "📊 Actualizando index.html con los últimos reportes..."
python3 actualizar_hub.py

echo ""
echo "📤 Commiteando y pusheando a GitHub..."
git add .
git commit -m "update: $(date '+%Y-%m-%d %H:%M')"
git push

echo ""
echo "✅ Listo. Netlify va a deployar en ~30 segundos."
