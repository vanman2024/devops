#!/bin/bash
# System Health Check for DevOps Environment
# Validates environment setup and dependency availability

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_check() { echo -e "${BLUE}[CHECK]${NC} $1"; }
print_pass() { echo -e "${GREEN}[PASS]${NC} $1"; }
print_fail() { echo -e "${RED}[FAIL]${NC} $1"; }
print_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

# Health check functions
check_python() {
    print_check "Checking Python installation..."
    if command -v python3 >/dev/null 2>&1; then
        local python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
        print_pass "Python 3 found: $python_version"
        return 0
    else
        print_fail "Python 3 not found - required for DevOps operations"
        return 1
    fi
}

check_git() {
    print_check "Checking Git installation..."
    if command -v git >/dev/null 2>&1; then
        local git_version=$(git --version | cut -d' ' -f3)
        print_pass "Git found: $git_version"
        return 0
    else
        print_fail "Git not found - required for version control"
        return 1
    fi
}

check_disk_space() {
    print_check "Checking available disk space..."
    local available=$(df "$REPO_ROOT" | tail -1 | awk '{print $4}')
    local available_gb=$((available / 1048576))
    
    if [ "$available_gb" -gt 1 ]; then
        print_pass "Sufficient disk space: ${available_gb}GB available"
        return 0
    else
        print_warn "Low disk space: ${available_gb}GB available"
        return 1
    fi
}

check_permissions() {
    print_check "Checking file permissions..."
    if [ -w "$REPO_ROOT" ]; then
        print_pass "Write permissions available"
        return 0
    else
        print_fail "No write permissions in $REPO_ROOT"
        return 1
    fi
}

# Main health check
main() {
    echo "🏥 DevOps Environment Health Check"
    echo "=================================="
    
    local failed_checks=0
    
    check_python || ((failed_checks++))
    check_git || ((failed_checks++))
    check_disk_space || ((failed_checks++))
    check_permissions || ((failed_checks++))
    
    echo "=================================="
    
    if [ "$failed_checks" -eq 0 ]; then
        print_pass "All health checks passed! Environment ready for DevOps operations."
        exit 0
    else
        print_fail "$failed_checks health check(s) failed. Please address issues above."
        exit 1
    fi
}

# Run if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi