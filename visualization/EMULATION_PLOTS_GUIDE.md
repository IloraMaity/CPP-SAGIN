# Mininet Emulation Plots Guide

This guide explains the two Mininet-specific plots and the data required to generate them.

## Overview

Two specialized plots validate the MATLAB cost models using empirical Mininet/Ryu emulation data:

1. **Plot 1: Empirical Breakdown of Flow Setup Latency** - Validates latency cost model components
2. **Plot 2: Controller CPU Load vs. Adaptation Events** - Validates reconfiguration overhead model

## Plot 1: Flow Setup Latency Breakdown

### Purpose
Breaks down total flow setup latency into measurable components to validate the MATLAB latency model:
- **Propagation & Transmission Delay**: Base latency from network links (2⋅l_ab[t]/c)
- **Controller Queuing Delay**: Time PACKET-IN waits in Ryu's input buffer (δ_ab^que[t])
- **Controller Processing Delay**: CPU time for path computation in Python code

### Required Data

For each time slot, collect:
```json
{
  "1": {
    "prop_trans_delay": 25.3,      // milliseconds - propagation + transmission
    "queuing_delay": 12.5,          // milliseconds - controller queue wait time
    "processing_delay": 5.2         // milliseconds - path computation time
  },
  "2": {
    ...
  }
}
```

### Data Collection Methods

#### 1. Propagation & Transmission Delay
- **Method A**: Calculate from link distances in topology
  ```python
  # From node positions and link distances
  prop_delay = 2 * (link_distance / c_light) * 1000  # ms
  trans_delay = (packet_size / link_bandwidth) * 1000  # ms
  prop_trans_delay = prop_delay + trans_delay
  ```

- **Method B**: Measure round-trip time (RTT) between switch and controller
  - Timestamp when PACKET-IN is sent from switch
  - Timestamp when FLOW-MOD is received at switch
  - Subtract queuing and processing delays (measured separately)

#### 2. Controller Queuing Delay
- **In Ryu Controller**: Log timestamps for PACKET-IN events
  ```python
  # In packet_in_handler:
  packet_in_time = time.time()  # When packet arrives at controller
  processing_start_time = time.time()  # When dequeued from buffer
  queuing_delay = (processing_start_time - packet_in_time) * 1000  # ms
  ```
- **Alternative**: Use Ryu's event queue statistics if available

#### 3. Controller Processing Delay
- **In Ryu Controller**: Measure time spent in path computation
  ```python
  # In packet_in_handler:
  processing_start_time = time.time()
  # ... path computation code ...
  processing_end_time = time.time()
  processing_delay = (processing_end_time - processing_start_time) * 1000  # ms
  ```

### Expected Behavior
- **Normal slots**: Queuing and processing delays should be low (< 20ms)
- **High-load slots**: Queuing delay should spike when controller is busy
- **Reconfiguration slots**: Processing delay should spike during GA/PAM execution

---

## Plot 2: CPU Load vs. Adaptation Events

### Purpose
Correlates algorithmic adaptation events with actual CPU resource usage, validating that high-cost events cause measurable CPU spikes.

### Required Data

For each time slot, collect:
```json
{
  "1": {
    "switch_handovers": 3,          // Count of low-cost remappings
    "full_reclustering": 0,          // Count of PAM re-clustering events
    "ga_reexecution": 0,             // Binary: 1 if GA Algorithm 1 executed
    "cpu_utilization": 35.2          // Percentage: average CPU usage during slot
  },
  "2": {
    ...
  }
}
```

### Data Collection Methods

#### 1. Adaptation Event Counts

**Switch Handovers (Low-cost)**
- Count nodes that change controller assignment without triggering re-clustering
- In orchestrator, when remapping occurs:
  ```python
  if not requires_reclustering(remapping):
      switch_handovers_count += 1
  ```

**Full Re-clustering (High-cost)**
- Count when PAM re-clustering algorithm is executed
- In orchestrator/controller, detect PAM execution:
  ```python
  if pam_clustering_executed:
      reclustering_count += 1
  ```

**GA Re-execution (High-cost)**
- Binary flag (0 or 1) indicating if Genetic Algorithm (Algorithm 1) executed
- In orchestrator, detect GA execution:
  ```python
  if ga_algorithm_executed:
      ga_reexecution = 1
  else:
      ga_reexecution = 0
  ```

#### 2. CPU Utilization

**Method A: System-level monitoring (Recommended)**
- Use `psutil` or system tools to monitor Ryu controller process
  ```python
  import psutil
  import time
  import os
  
  # Get Ryu process
  ryu_pid = find_ryu_process_pid()
  process = psutil.Process(ryu_pid)
  
  # Sample CPU usage over time slot
  cpu_samples = []
  start_time = time.time()
  slot_duration = 60  # seconds
  
  while time.time() - start_time < slot_duration:
      cpu_samples.append(process.cpu_percent(interval=1))
      time.sleep(1)
  
  avg_cpu = sum(cpu_samples) / len(cpu_samples)
  ```

**Method B: Docker container stats** (if using Docker)
  ```bash
  # Monitor controller container
  docker stats --format "{{.CPUPerc}}" ryu-controller | \
      awk '{sum+=$1; count++} END {print sum/count}'
  ```

**Method C: Process CPU time** (alternative)
  ```python
  import resource
  import time
  
  start_time = time.time()
  start_cpu = resource.getrusage(resource.RUSAGE_SELF).ru_utime
  
  # ... slot execution ...
  
  end_cpu = resource.getrusage(resource.RUSAGE_SELF).ru_utime
  elapsed_time = time.time() - start_time
  cpu_percent = ((end_cpu - start_cpu) / elapsed_time) * 100
  ```

### Expected Behavior
- **Normal slots**: CPU should be stable (~20-40%) with only switch handovers
- **Re-clustering slots**: CPU should spike to ~50-70% during PAM execution
- **GA execution slots**: CPU should spike dramatically to ~80-95% during GA re-execution
- **Correlation**: High-cost events (bars) should align with CPU spikes (line)

---

## Data File Format

Create `emulation_metrics.json` in the orchestrator or results directory:

```json
{
  "1": {
    "prop_trans_delay": 25.3,
    "queuing_delay": 12.5,
    "processing_delay": 5.2,
    "switch_handovers": 3,
    "full_reclustering": 0,
    "ga_reexecution": 0,
    "cpu_utilization": 35.2
  },
  "2": {
    "prop_trans_delay": 28.1,
    "queuing_delay": 8.3,
    "processing_delay": 4.8,
    "switch_handovers": 2,
    "full_reclustering": 0,
    "ga_reexecution": 0,
    "cpu_utilization": 32.1
  },
  "3": {
    "prop_trans_delay": 22.7,
    "queuing_delay": 45.2,
    "processing_delay": 125.3,
    "switch_handovers": 1,
    "full_reclustering": 1,
    "ga_reexecution": 0,
    "cpu_utilization": 68.5
  },
  "4": {
    "prop_trans_delay": 24.9,
    "queuing_delay": 78.4,
    "processing_delay": 342.1,
    "switch_handovers": 0,
    "full_reclustering": 0,
    "ga_reexecution": 1,
    "cpu_utilization": 89.2
  }
}
```

**Notes:**
- Time slots can be strings ("1", "2") or array indices (0, 1, 2...)
- Missing fields default to 0
- At least 25 slots recommended for meaningful plots

---

## Generating Plots

### Using Command Line

```bash
# Generate both emulation plots
python visualization/visualize_results.py --all

# Generate only flow latency plot
python visualization/visualize_results.py --flow-latency

# Generate only CPU vs adaptation plot
python visualization/visualize_results.py --cpu-adaptation

# Specify custom metrics file
python visualization/visualize_results.py --all \
    --emulation-metrics results/my_emulation_metrics.json
```

### Using Python API

```python
from visualization.visualize_results import SAGINVisualizer

visualizer = SAGINVisualizer('mininet_topology_data.json')

# Generate Plot 1
visualizer.plot_flow_setup_latency_breakdown(
    'emulation_metrics.json',
    output_file='flow_latency.png',
    num_slots=25
)

# Generate Plot 2
visualizer.plot_controller_cpu_vs_adaptation_events(
    'emulation_metrics.json',
    output_file='cpu_adaptation.png',
    num_slots=25
)
```

---

## Plot Interpretation

### Plot 1: Flow Setup Latency Breakdown

**Validation Criteria:**
- Total latency (sum of components) should match MATLAB estimates (±20%)
- Queuing delay should spike during high-load slots (when controller is busy)
- Processing delay should spike during reconfiguration slots (GA/PAM execution)
- Propagation delay should be relatively constant (network structure unchanged)

**Red Flags:**
- Processing delay > 200ms suggests inefficient path computation
- Queuing delay > 100ms suggests controller overload
- Inconsistent total latency vs MATLAB suggests model mismatch

### Plot 2: CPU Load vs. Adaptation Events

**Validation Criteria:**
- CPU should correlate with event type:
  - Switch handovers: Low CPU (< 50%)
  - Re-clustering: Medium CPU (50-70%)
  - GA execution: High CPU (70-95%)
- CPU spikes should align temporally with high-cost events
- Baseline CPU (no events) should be stable (~20-40%)

**Red Flags:**
- CPU > 95% suggests controller overload
- CPU spikes without corresponding events suggest background processes
- No correlation between events and CPU suggests measurement error

---

## Implementation Suggestions

### Where to Add Logging (Without Changing Controller Script)

Since you don't want to modify `comosat_controller.py`, consider:

1. **Wrapper Script**: Create a wrapper around the orchestrator that:
   - Monitors Ryu process CPU usage
   - Intercepts PACKET-IN events via Ryu logs
   - Correlates timestamps to extract delays

2. **External Monitoring**: Use system tools:
   - `top`, `htop`, `psutil` for CPU monitoring
   - `tcpdump` or `wireshark` for packet-level analysis
   - Log parsing for event detection

3. **Orchestrator Extension**: Modify `orchestrator.py` to:
   - Track adaptation events (already has remapping detection)
   - Monitor CPU using `psutil`
   - Export metrics to JSON

4. **Minimal Controller Logging**: Add minimal timestamps to controller log messages:
   - Log PACKET-IN arrival time
   - Log FLOW-MOD send time
   - Parse logs post-execution to extract metrics

### Recommended Approach

1. **Extend orchestrator.py** to collect CPU metrics (no controller changes)
2. **Add log parsing** to extract timing from existing Ryu logs
3. **Use topology data** to calculate propagation delays
4. **Infer events** from topology changes (already tracked)

---

## Additional Plot Suggestions

Consider these complementary plots for complete validation:

### Plot 3: Queuing Delay vs. Arrival Rate
- X-axis: PACKET-IN arrival rate (packets/sec)
- Y-axis: Mean queuing delay (ms)
- **Purpose**: Validate M/M/1 queuing model assumption

### Plot 4: Processing Delay vs. Network Size
- X-axis: Number of nodes in domain
- Y-axis: Mean processing delay (ms)
- **Purpose**: Validate computational complexity model

### Plot 5: Total Latency: MATLAB vs. Emulation
- X-axis: Time slot
- Y-axis: Latency (ms)
- Two lines: MATLAB estimate vs. Emulation measurement
- **Purpose**: Direct validation of overall cost model

These can be added later if needed.

