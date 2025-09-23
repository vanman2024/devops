#!/bin/bash
# Performance Monitoring Script for DevOps Operations
# Tracks execution times, memory usage, and system performance

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../../.." && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_metric() { echo -e "${BLUE}[PERF]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARN]${NC} $1"; }
print_success() { echo -e "${GREEN}[PASS]${NC} $1"; }

# Performance monitoring functions
monitor_memory() {
    local process_name="$1"
    if command -v ps >/dev/null 2>&1; then
        local memory_usage=$(ps aux | grep "$process_name" | grep -v grep | awk '{sum+=$4} END {print sum}')
        if [ -n "$memory_usage" ]; then
            print_metric "Memory usage for $process_name: ${memory_usage}%"
        fi
    fi
}

monitor_disk_usage() {
    local path="${1:-$REPO_ROOT}"
    if command -v du >/dev/null 2>&1; then
        local disk_usage=$(du -sh "$path" 2>/dev/null | cut -f1)
        print_metric "Disk usage for $path: $disk_usage"
    fi
}

benchmark_operations() {
    print_metric "Running performance benchmarks..."
    
    # Test file I/O performance
    local start_time=$(date +%s.%3N)
    echo "Performance test" > /tmp/perf_test_$$
    cat /tmp/perf_test_$$ > /dev/null
    rm -f /tmp/perf_test_$$
    local end_time=$(date +%s.%3N)
    local io_duration=$(echo "$end_time - $start_time" | bc -l 2>/dev/null || echo "0.001")
    print_metric "File I/O benchmark: ${io_duration}s"
    
    if (( $(echo "$io_duration > 0.1" | bc -l 2>/dev/null || echo 0) )); then
        print_warning "I/O performance slower than expected (>0.1s)"
    else
        print_success "I/O performance within acceptable range"
    fi
}

# Main execution
main() {
    echo "🚀 DevOps Performance Monitor v1.0"
    echo "=================================="
    
    print_metric "Repository: $(basename "$REPO_ROOT")"
    print_metric "Timestamp: $(date)"
    
    monitor_disk_usage "$REPO_ROOT"
    benchmark_operations
    
    echo "=================================="
    print_success "Performance monitoring complete"
}

# Run if called directly
if [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    main "$@"
fi