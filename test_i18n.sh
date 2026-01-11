#!/bin/bash

# i18n Integration Test Script
# Tests bilingual support (English/Spanish) with accessibility verification

set -e

echo "=================================================="
echo "i18n Integration Test Suite"
echo "=================================================="
echo ""

BACKEND_URL="http://127.0.0.1:8000"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
    local test_name="$1"
    local command="$2"
    local expected_lang="$3"

    echo "---"
    echo "Test: $test_name"
    echo "Command: $command"

    response=$(eval "$command" 2>/dev/null)

    if [ $? -eq 0 ]; then
        detected_lang=$(echo "$response" | python3 -c "import sys, json; print(json.load(sys.stdin).get('language', 'none'))" 2>/dev/null)

        if [ "$detected_lang" = "$expected_lang" ]; then
            echo -e "${GREEN}✓ PASSED${NC} - Language: $detected_lang"
            ((TESTS_PASSED++))
        else
            echo -e "${RED}✗ FAILED${NC} - Expected: $expected_lang, Got: $detected_lang"
            ((TESTS_FAILED++))
        fi
    else
        echo -e "${RED}✗ FAILED${NC} - Request failed"
        ((TESTS_FAILED++))
    fi

    echo ""
}

echo "1. English Input → English Output"
echo "=================================================="

run_test \
    "Simple English question" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"What is the store policy?\", \"store_id\": \"1234\"}'" \
    "en"

run_test \
    "Technical English query" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"How do I reset the kiosk system?\", \"store_id\": \"1234\"}'" \
    "en"

run_test \
    "Inventory English query" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"What is the current stock level for item 12345?\", \"store_id\": \"1234\"}'" \
    "en"

echo ""
echo "2. Spanish Input → Spanish Output"
echo "=================================================="

run_test \
    "Simple Spanish question" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"¿Cuál es la política de la tienda?\", \"store_id\": \"1234\"}'" \
    "es"

run_test \
    "Technical Spanish query" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"¿Cómo reinicio el sistema del quiosco?\", \"store_id\": \"1234\"}'" \
    "es"

run_test \
    "Inventory Spanish query" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"¿Cuál es el nivel de inventario del artículo 12345?\", \"store_id\": \"1234\"}'" \
    "es"

run_test \
    "Spanish without accents" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"Donde esta el inventario de la tienda?\", \"store_id\": \"1234\"}'" \
    "es"

echo ""
echo "3. Mixed Language Input → Correct Fallback"
echo "=================================================="

run_test \
    "English dominant (mixed)" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"What es the store policy today?\", \"store_id\": \"1234\"}'" \
    "en"

run_test \
    "Spanish dominant (mixed)" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"¿Cuál is the política de devoluciones?\", \"store_id\": \"1234\"}'" \
    "es"

echo ""
echo "4. Edge Cases"
echo "=================================================="

run_test \
    "Numbers only (defaults to English)" \
    "curl -s -X POST $BACKEND_URL/ask -H 'Content-Type: application/json' -d '{\"question\": \"12345 67890\", \"store_id\": \"1234\"}'" \
    "en"

echo ""
echo "=================================================="
echo "Test Results"
echo "=================================================="
echo -e "${GREEN}Passed: $TESTS_PASSED${NC}"
echo -e "${RED}Failed: $TESTS_FAILED${NC}"

TOTAL=$((TESTS_PASSED + TESTS_FAILED))
echo "Total:  $TOTAL"

if [ $TESTS_FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ All tests passed!${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}✗ Some tests failed.${NC}"
    exit 1
fi
