# SAGIN Network Mininet/Ryu Implementation

This project implements a demonstration of the COMOSAT (Controller Placement Optimization for Satellite Networks) algorithm using Mininet for network emulation and Ryu for SDN control.

## Overview

This implementation demonstrates:
- Export of MATLAB simulation data to network emulation format
- Dynamic SAGIN network topology with Mininet
- Hierarchical SDN controller placement with Ryu
- Empirical validation of MATLAB cost models
- Generation of 6 journal-ready plots

### Key Features

- ✅ Dynamic topology management across time slots
- ✅ Domain-based hierarchical control
- ✅ Performance metrics collection
- ✅ Automatic plot generation (6 journal plots)
- ✅ Docker support for easy deployment

---

## Architecture

- **Satellites (LEO/MEO), HAPS, Ground Stations** → Mininet switches
- **Single Ryu Controller** → Emulates hierarchical controller logic
- **Links** → Mininet links with configurable delay/bandwidth
- **Topology Changes** → Time-slotted updates via controller

**Note**: Uses a single Ryu controller instance that logically manages multiple domains. The hierarchical structure (domain controllers + master controllers) from COMOSAT is emulated within this single controller.

### Components

- **MATLAB Export** (`matlab_export/`): Exports simulation data to JSON
- **Mininet Topology** (`topology/`): Custom topology class for SAGIN networks
- **Ryu Controller** (`controller/`): SDN controller application
- **Orchestrator** (`orchestrator/`): Coordinates simulation across time slots
- **Visualization** (`visualization/`): Generates 6 journal-ready plots

---

## Prerequisites

- **Python 3.8+** with packages: `mininet`, `ryu`, `matplotlib`, `numpy`, `networkx`, `psutil`
- **MATLAB R2020b+** (for data export) with Aerospace and Mapping Toolboxes
- **Docker 20.10+** and **Docker Compose 2.0+** (recommended)

---

## Installation

### Python Dependencies

```bash
pip install -r requirements.txt
```

### Docker (Recommended)

No additional installation needed. Docker handles all dependencies.

---

## Quick Start

### Step 1: Export Data from MATLAB

```matlab
% From project root directory
addpath('mininet_ryu_comosat/matlab_export');
run_comosat_and_export(10)  % 10 time slots
```

This generates `topology/mininet_topology_data.json`.

### Step 2: Run with Docker

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
- **Plots**: `plots/*.png` (6 journal plots generated automatically)

---

## Execution Methods

### Method 1: Docker (Recommended)

**Quick Start:**
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

---

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

---

### Method 3: Separate VMs (Distributed)

**VM Setup:**
- Both VMs: VirtualBox → Network → Adapter 2: Internal Network (`sagin-network`)
- **Ryu VM (IP: 192.168.199.3):**
  ```bash
  sudo nmcli device set enp0s8 managed no
  sudo ifconfig enp0s8 192.168.199.3 netmask 255.255.255.0 up
  ```

- **Mininet VM:**
  ```bash
  sudo nmcli device set enp0s8 managed no
  sudo ifconfig enp0s8 192.168.199.20 netmask 255.255.255.0 up
  ping 192.168.199.3  # Test connectivity
  ```

**Execution:**
- **Ryu VM:** `ryu-manager --verbose --ofp-listen-host 0.0.0.0 comosat_controller.py`
- **Mininet VM:** `python3 orchestrator.py --slots 10 --remote-controller-ip 192.168.199.3`

---

## Visualization

### Automatic Generation (Docker)

Plots are generated automatically after simulation completes when using Docker.

### Manual Generation

```bash
cd mininet_ryu_comosat/visualization
python3 visualize_results.py --all --output ../plots/
```

### Generated Plots (6 Journal Plots)

1. **MATLAB vs. Mininet Comparison** (`matlab_vs_mininet_comparison.png`)
   - Validates MATLAB cost model accuracy

2. **Flow Setup Latency Breakdown** (`flow_setup_latency_breakdown.png`)
   - Empirical breakdown of latency components

3. **Remapping Statistics** (`remapping_statistics.png`)
   - Controller remappings and domain evolution

4. **CPU Load vs. Adaptation Events** (`controller_cpu_vs_adaptation.png`)
   - Resource usage correlation with adaptation events

5. **Controller Evolution** (`controller_evolution.png`)
   - Topology evolution across 4 selected time slots

6. **Queuing Delay vs. Arrival Rate** (`queuing_delay_vs_arrival_rate.png`)
   - Validates M/M/1 queuing model assumption

**Note**: Plots 1, 2, 4, and 6 require `emulation_metrics.json` for full functionality. See `visualization/EMULATION_PLOTS_GUIDE.md` for data collection instructions.

---

## File Structure

```
mininet_ryu_comosat/
├── matlab_export/          # MATLAB data export scripts
├── topology/               # Mininet topology builder
├── controller/             # Ryu SDN controller
├── orchestrator/           # Simulation orchestrator
├── visualization/          # Plot generation (6 journal plots)
├── experiments/            # Execution scripts
├── plots/                  # Generated plots (output)
├── results/                # Simulation metrics (output)
├── docker-compose.yml      # Docker configuration
├── Dockerfile.*            # Container definitions
└── requirements.txt        # Python dependencies
```

---

## Troubleshooting

### Common Issues

**"Permission denied" (Linux)**
- Solution: Run with `sudo` (e.g., `sudo python3 orchestrator.py`)

**"Read-only file system" (Docker)**
- Solution: Metrics are written to `results/` directory (writable volume)

**"Topology file not found"**
- Solution: Run MATLAB export script first

**"Cannot reach Ryu VM" (Distributed)**
- Solution: Check IP configuration and firewall (`sudo ufw allow 6633/tcp`)

**"Container won't start" (Docker)**
- Solution: Check logs: `docker compose logs`

---

## Limitations

This is a partial implementation for demonstration:

1. Discrete time slots (not continuous movement)
2. Link delays based on geometric distance only
3. Limited scale: Maximum 60 nodes
4. Pre-computed controller placements from MATLAB
5. Single controller instance (hierarchical structure emulated)

---

## Output Files

### Generated Plots (`plots/`)
- 6 journal-ready plots (see [Visualization](#visualization) section)

### Metrics (`results/`)
- `simulation_metrics.json`: Remappings, domains, network statistics per slot

---

## Research Paper Usage

For journal paper recommendations, see `JOURNAL_PLOT_RECOMMENDATIONS.md`.

### Citation

```bibtex
@software{sagin_mininet_ryu,
  title={SAGIN Network Mininet/Ryu Implementation for COMOSAT},
  author={Research Team},
  year={2024}
}
```

---

## License

[Specify your license here]

---

## Acknowledgments

This implementation is part of research on SDN controller placement in Space-Air-Ground Integrated Networks (SAGIN).
