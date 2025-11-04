# SAGIN Network Mininet/Ryu Implementation

COMOSAT (Controller Placement Optimization for Satellite Networks) implementation using Mininet for network emulation and Ryu for SDN control. Demonstrates dynamic topology management and empirical validation of MATLAB cost models.

## Overview

- Export of MATLAB simulation data to network emulation format
- Dynamic SAGIN network topology with Mininet
- Hierarchical SDN controller placement with Ryu
- Automatic generation of 6 journal-ready plots

## Quick Start

### Step 1: Export Data from MATLAB

```matlab
% From project root directory
addpath('mininet_ryu_comosat/matlab_export');
run_comosat_and_export(10)  % 10 time slots
```

This generates `topology/mininet_topology_data.json`.

### Step 2: Run with Docker (Recommended)

```powershell
# Windows (PowerShell)
cd "path\to\mininet_ryu_comosat"
docker compose up
```

```bash
# Linux/Mac
cd mininet_ryu_comosat
docker compose up
```

### Step 3: View Results

After simulation completes:
- **Metrics**: `results/simulation_metrics.json`
- **Plots**: `plots/*.png` (6 plots generated automatically)

## Architecture

- **Satellites (LEO/MEO), HAPS, Ground Stations** → Mininet switches
- **Single Ryu Controller** → Emulates hierarchical controller logic
- **Time-slotted topology updates** via controller

**Components**: MATLAB Export, Mininet Topology, Ryu Controller, Orchestrator, Visualization

## Installation

### Prerequisites

- **Python 3.8+** with packages: `mininet`, `ryu`, `matplotlib`, `numpy`, `networkx`, `psutil`
- **MATLAB R2020b+** (for data export) with Aerospace and Mapping Toolboxes
- **Docker 20.10+** and **Docker Compose 2.0+** (recommended)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## Execution Methods

### Method 1: Docker (Recommended)

```bash
cd mininet_ryu_comosat
docker compose up
```

**Custom Configuration:**
Edit `docker-compose.yml`:
```yaml
command: python3 orchestrator/orchestrator.py --slots 10 --duration 60
```

**Docker Commands:**
```bash
docker compose build          # Build containers
docker compose up -d          # Run in background
docker compose logs -f        # View logs
docker compose down           # Stop services
```

### Method 2: Single VM (Local)

**Terminal 1: Start Ryu Controller**
```bash
cd mininet_ryu_comosat/controller
ryu-manager --verbose comosat_controller.py
```

**Terminal 2: Run Orchestrator**
```bash
cd mininet_ryu_comosat/orchestrator
python3 orchestrator.py --slots 10 --duration 60
```

### Method 3: Separate VMs (Distributed)

**Setup:**
- Both VMs: VirtualBox → Network → Adapter 2: Internal Network (`sagin-network`)
- **Ryu VM (IP: 192.168.199.3):** `sudo ifconfig enp0s8 192.168.199.3 netmask 255.255.255.0 up`
- **Mininet VM:** `sudo ifconfig enp0s8 192.168.199.20 netmask 255.255.255.0 up`

**Execution:**
- **Ryu VM:** `ryu-manager --verbose --ofp-listen-host 0.0.0.0 comosat_controller.py`
- **Mininet VM:** `python3 orchestrator.py --slots 10 --remote-controller-ip 192.168.199.3`

## Visualization

### Automatic Generation (Docker)

Plots are generated automatically after simulation completes.

### Manual Generation

```bash
cd mininet_ryu_comosat/visualization
python3 visualize_results.py --all --output ../plots/
```

### Generated Plots (6 Plots)

1. **MATLAB vs. Mininet Comparison** - Validates MATLAB cost model accuracy
2. **Flow Setup Latency Breakdown** - Empirical breakdown of latency components
3. **Remapping Statistics** - Controller remappings and domain evolution
4. **CPU Load vs. Adaptation Events** - Resource usage correlation
5. **Controller Evolution** - Topology evolution across 4 time slots
6. **Queuing Delay vs. Arrival Rate** - Validates M/M/1 queuing model

**Note**: Plots 1, 2, 4, and 6 require `emulation_metrics.json`. See `visualization/EMULATION_PLOTS_GUIDE.md` for data collection.

## File Structure

```
mininet_ryu_comosat/
├── matlab_export/          # MATLAB data export scripts
├── topology/               # Mininet topology builder
├── controller/             # Ryu SDN controller
├── orchestrator/           # Simulation orchestrator
├── visualization/          # Plot generation (6 plots)
├── experiments/            # Execution scripts
├── plots/                  # Generated plots (output)
├── results/                # Simulation metrics (output)
├── docker-compose.yml      # Docker configuration
├── Dockerfile.*            # Container definitions
└── requirements.txt        # Python dependencies
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Permission denied" (Linux) | Run with `sudo` |
| "Read-only file system" (Docker) | Metrics written to `results/` (writable) |
| "Topology file not found" | Run MATLAB export script first |
| "Cannot reach Ryu VM" | Check IP and firewall (`sudo ufw allow 6633/tcp`) |
| "Container won't start" | Check logs: `docker compose logs` |

## Limitations

Partial implementation for demonstration:
- Discrete time slots (not continuous movement)
- Link delays based on geometric distance only
- Limited scale: Maximum 60 nodes
- Pre-computed controller placements from MATLAB
- Single controller instance (hierarchical structure emulated)

## Output Files

- **Plots** (`plots/`): 6 generated plots (see [Visualization](#visualization))
- **Metrics** (`results/`): `simulation_metrics.json` with remappings, domains, statistics per slot

## Citation

```bibtex
@software{sagin_mininet_ryu,
  title={SAGIN Network Mininet/Ryu Implementation for Controller Placement},
  author={Ilora Maity},
  year={2024}
}
```

## License

[Specify your license here]

## Acknowledgments

This implementation is part of research on SDN controller placement in Space-Air-Ground Integrated Networks (SAGIN).
