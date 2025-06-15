#!/bin/bash


set -e

echo "Uruchamianie testów RAG..."

if [ -f ".env" ]; then
    echo "Wczytywanie zmiennych z .env..."
    source .env

    if [ -z "$OPENAI_API_KEY" ]; then
        echo "OPENAI_API_KEY nie jest ustawiony w .env"
        exit 1
    else
        echo "OPENAI_API_KEY wczytany"
    fi
else
    echo "Plik .env nie istnieje. Sprawdzam zmienną środowiskową..."
    if [ -z "$OPENAI_API_KEY" ]; then
        echo "OPENAI_API_KEY nie jest ustawiony!"
        echo "Stwórz plik .env z OPENAI_API_KEY=twój-klucz"
        exit 1
    fi
fi

CONFIG_FILE="promptfooconfig.yaml"
if [ ! -f "$CONFIG_FILE" ]; then

    if [ -f "promptfoo.config.yaml" ]; then
        CONFIG_FILE="promptfoo.config.yaml"
    elif [ -f ".promptfoo.yaml" ]; then
        CONFIG_FILE=".promptfoo.yaml"
    elif [ -f "promptfoo.yaml" ]; then
        CONFIG_FILE="promptfoo.yaml"
    else
        echo "❌ Nie znaleziono pliku konfiguracyjnego!"
        echo "Oczekiwane nazwy: promptfooconfig.yaml, promptfoo.config.yaml, .promptfoo.yaml"
        exit 1
    fi
fi

echo "Używam konfiguracji: $CONFIG_FILE"

if ! command -v promptfoo &> /dev/null; then
    echo "promptfoo nie jest zainstalowany!"
    echo "Zainstaluj go przez: npm install -g promptfoo"
    exit 1
fi

echo "Informacje o testach:"
echo "   - Konfiguracja: $CONFIG_FILE"
echo "   - API Key: ${OPENAI_API_KEY:0:8}..."
echo "   - Data: $(date)"
echo ""

echo "Uruchamianie testów..."
promptfoo eval -c "$CONFIG_FILE" "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "Testy zakończone pomyślnie!"
    echo ""
    echo "Aby zobaczyć wyniki w przeglądarce:"
    echo "   promptfoo view"
    echo ""
    echo "Wyniki zapisane w: ./promptfoo-results"
else
    echo ""
    echo "Testy zakończone z błędami!"
    exit 1
fi