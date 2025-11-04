#!/bin/bash
# =========================================================================
# run_distributed.sh
# =========================================================================
# Run COMOSAT simulation with Mininet on one VM and Ryu on another VM
#
# USAGE:
#   On Mininet VM:
#     ./run_distributed.sh --mininet --ryu-ip <RYU_VM_IP>
#
#   On Ryu VM:
#     ./run_distributed.sh --ryu
# =========================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Default configuration
RYU_IP="192.168.199.3"
RYU_PORT=6633
NUM_SLOTS=10
SLOT_DURATION=60
TOPOLOGY_JSON="mininet_topology_data.json"

# Parse arguments
MODE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --ryu)
            MODE="ryu"
            shift
            ;;
        --mininet)
            MODE="mininet"
            shift
            ;;
        --ryu-ip)
            RYU_IP="$2"
            shift 2
            ;;
        --ryu-port)
            RYU_PORT="$2"
            shift 2
            ;;
        --slots)
            NUM_SLOTS="$2"
            shift 2
            ;;
        --duration)
            SLOT_DURATION="$2"
            shift 2
            ;;
        --help)
            echo "Usage:"
            echo "  On Ryu VM:    ./run_distributed.sh --ryu"
            echo "  On Mininet VM: ./run_distributed.sh --mininet --ryu-ip <IP>"
            echo ""
            echo "Options:"
            echo "  --ryu              Start Ryu controller mode"
            echo "  --mininet          Start Mininet mode"
            echo "  --ryu-ip IP        IP address of Ryu VM (default: 192.168.199.3)"
            echo "  --ryu-port PORT    Port of Ryu controller (default: 6633)"
            echo "  --slots N          Number of time slots (default: 10)"
            echo "  --duration SEC     Slot duration in seconds (default: 60)"
            echo "  --help             Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

if [[ -z "$MODE" ]]; then
    echo "Error: Must specify --ryu or --mininet"
    echo "Use --help for usage information"
    exit 1
fi

cd "$PROJECT_ROOT"

if [[ "$MODE" == "ryu" ]]; then
    # =========================================================================
    # RYU VM MODE
    # =========================================================================
    echo "========================================================================="
    echo "Starting Ryu Controller on Ryu VM"
    echo "========================================================================="
    echo ""
    echo "Configuration:"
    echo "  Listening on: 0.0.0.0 (all interfaces)"
    echo "  Port: $RYU_PORT"
    echo "  Controller: comosat_controller.py"
    echo ""
    echo "Press Ctrl+C to stop"
    echo "========================================================================="
    
    # Check if topology data exists (for controller initialization)
    if [[ -f "topology/$TOPOLOGY_JSON" ]]; then
        echo "Topology data found: topology/$TOPOLOGY_JSON"
    else
        echo "Warning: Topology data not found. Controller will start but may need manual configuration."
    fi
    
    # Start Ryu controller
    cd controller
    ryu-manager --verbose --ofp-listen-host 0.0.0.0 comosat_controller.py
    
elif [[ "$MODE" == "mininet" ]]; then
    # =========================================================================
    # MININET VM MODE
    # =========================================================================
    echo "========================================================================="
    echo "Starting Mininet Simulation on Mininet VM"
    echo "========================================================================="
    echo ""
    echo "Configuration:"
    echo "  Remote Ryu IP: $RYU_IP"
    echo "  Remote Ryu Port: $RYU_PORT"
    echo "  Time Slots: $NUM_SLOTS"
    echo "  Slot Duration: ${SLOT_DURATION}s"
    echo ""
    
    # Check if topology file exists
    if [[ ! -f "topology/$TOPOLOGY_JSON" ]]; then
        echo "Error: Topology file not found: topology/$TOPOLOGY_JSON"
        echo "Please run MATLAB export first."
        exit 1
    fi
    
    # Verify connectivity to Ryu VM
    echo "Testing connectivity to Ryu VM ($RYU_IP)..."
    if ping -c 2 "$RYU_IP" &> /dev/null; then
        echo "✓ Can reach Ryu VM"
    else
        echo "✗ Cannot reach Ryu VM at $RYU_IP"
        echo "Please check:"
        echo "  1. Ryu VM is running and network configured"
        echo "  2. IP address is correct"
        echo "  3. Firewall allows connections"
        exit 1
    fi
    
    # Run orchestrator
    echo ""
    echo "Starting simulation..."
    echo "========================================================================="
    
    cd orchestrator
    python3 orchestrator.py \
        --slots "$NUM_SLOTS" \
        --duration "$SLOT_DURATION" \
        --remote-controller-ip "$RYU_IP" \
        --remote-controller-port "$RYU_PORT"
    
    echo ""
    echo "========================================================================="
    echo "Simulation Complete!"
    echo "========================================================================="
    echo ""
    echo "Results:"
    echo "  Metrics: orchestrator/simulation_metrics.json"
    echo ""
    echo "To generate visualizations:"
    echo "  cd ../visualization"
    echo "  python3 visualize_results.py --all --output ../plots/"
fi

