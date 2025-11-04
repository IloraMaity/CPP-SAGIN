#!/bin/bash
# =========================================================================
# run_experiment.sh
# =========================================================================
# Automated experiment runner for SAGIN network simulation
#
# This script orchestrates the complete workflow:
# 1. Export data from MATLAB
# 2. Run Mininet simulation with Ryu controller
# 3. Collect results
# 4. Generate visualizations
# =========================================================================

set -e  # Exit on error

# Configuration
MATLAB_ROOT="/path/to/matlab"  # Update with your MATLAB path
NUM_SLOTS=10
SLOT_DURATION=60  # seconds
ALGORITHM="KMPP"  # KMPP, COMOSAT, MCD, or HDS

# Directories
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
MATLAB_DIR="$PROJECT_ROOT/matlab_export"
TOPO_DIR="$PROJECT_ROOT/topology"
ORCHESTRATOR_DIR="$PROJECT_ROOT/orchestrator"
VISUALIZATION_DIR="$PROJECT_ROOT/visualization"
PLOTS_DIR="$PROJECT_ROOT/plots"

echo "========================================================================="
echo "SAGIN Network Simulation Experiment Runner"
echo "========================================================================="

# Step 1: Export data from MATLAB
echo ""
echo "Step 1: Exporting data from MATLAB..."
echo "----------------------------------------------------------------------"

cd "$MATLAB_DIR"

# Check if MATLAB is available
if [ ! -f "$MATLAB_ROOT/bin/matlab" ]; then
    echo "Warning: MATLAB not found at $MATLAB_ROOT"
    echo "Skipping MATLAB export step."
    echo "Make sure to run MATLAB export manually if needed."
else
    "$MATLAB_ROOT/bin/matlab" -batch "run_simulation_and_export('$ALGORITHM', $NUM_SLOTS)"
fi

# Verify export file exists
EXPORT_FILE="$TOPO_DIR/mininet_topology_data.json"
if [ ! -f "$EXPORT_FILE" ]; then
    echo "Error: Topology export file not found: $EXPORT_FILE"
    echo "Please run the MATLAB export script first."
    exit 1
fi

echo "Data export complete."

# Step 2: Check dependencies
echo ""
echo "Step 2: Checking dependencies..."
echo "----------------------------------------------------------------------"

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 not found. Please install Python 3."
    exit 1
fi

# Check for Mininet
if ! command -v mn &> /dev/null; then
    echo "Error: Mininet not found. Please install Mininet."
    exit 1
fi

# Check for Ryu
if ! command -v ryu-manager &> /dev/null; then
    echo "Error: Ryu controller not found. Please install Ryu."
    exit 1
fi

echo "All dependencies found."

# Step 3: Create output directories
echo ""
echo "Step 3: Creating output directories..."
echo "----------------------------------------------------------------------"

mkdir -p "$PLOTS_DIR"
echo "Output directory: $PLOTS_DIR"

# Step 4: Run simulation
echo ""
echo "Step 4: Running Mininet simulation..."
echo "----------------------------------------------------------------------"

cd "$ORCHESTRATOR_DIR"
python3 orchestrator.py --slots $NUM_SLOTS --duration $SLOT_DURATION

echo "Simulation complete."

# Step 5: Generate visualizations
echo ""
echo "Step 5: Generating visualizations..."
echo "----------------------------------------------------------------------"

cd "$VISUALIZATION_DIR"
python3 visualize_results.py --all --output "$PLOTS_DIR"

echo "Visualizations complete."

# Step 6: Summary
echo ""
echo "========================================================================="
echo "Experiment Complete!"
echo "========================================================================="
echo ""
echo "Results:"
echo "  - Topology data: $EXPORT_FILE"
echo "  - Simulation metrics: $ORCHESTRATOR_DIR/simulation_metrics.json"
echo "  - Visualizations: $PLOTS_DIR/"
echo ""
echo "Generated files:"
ls -lh "$PLOTS_DIR"
echo ""
echo "========================================================================="

