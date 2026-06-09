#!/bin/bash
# Auto-deploy del hub Market-hub.
# Lo dispara launchd automáticamente cuando aparece/cambia un archivo en semanales/.
# Regenera index.html y pushea a GitHub -> Netlify deploya.

export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"
DIR="/Users/mateomurray/Desktop/Digests/Market Analysis"
LOG="$DIR/.deploy.log"

cd "$DIR" || exit 1

echo "=== $(date '+%Y-%m-%d %H:%M:%S') · trigger ===" >> "$LOG"

# Esperar a que el archivo termine de escribirse antes de procesar
sleep 5

# Regenerar el index del hub con los últimos reportes
python3 actualizar_hub.py >> "$LOG" 2>&1

# ¿Hay cambios para publicar?
if [[ -n "$(git status --porcelain)" ]]; then
  git add . >> "$LOG" 2>&1
  git commit -m "auto-deploy: $(date '+%Y-%m-%d %H:%M')" >> "$LOG" 2>&1
  if git push >> "$LOG" 2>&1; then
    echo ">>> push OK · Netlify deployando" >> "$LOG"
  else
    echo "!!! push FALLÓ (revisar credenciales git / red)" >> "$LOG"
  fi
else
  echo ">>> sin cambios, nada que pushear" >> "$LOG"
fi
echo "" >> "$LOG"
