# Journal Paper Plot Recommendations

## Recommended Plots for COMOSAT Mininet/Ryu Validation Paper

This document provides recommendations for plots to include in your journal paper, organized by priority and research contribution.

---

## 📊 Priority 1: Essential Plots (Must Include)

### Plot 1: MATLAB vs. Mininet Emulation Comparison
**Title**: "Flow Setup Latency: Theoretical Model vs. Empirical Measurement"

**Purpose**: Direct validation of MATLAB cost model accuracy

**Visualization**:
- **X-axis**: Time Slot (1 to 25)
- **Y-axis**: Total Flow Setup Latency (milliseconds)
- **Two line plots**:
  - MATLAB estimated latency (dashed blue line, ▲ markers)
  - Mininet measured latency (solid red line, ● markers)
- **Shaded region**: ±10% error bounds around MATLAB estimate
- **Subplot**: Absolute error (MATLAB - Mininet) per slot

**Why Essential**:
- ✅ **Core validation**: Directly shows MATLAB model accuracy
- ✅ **Research contribution**: Demonstrates empirical validation
- ✅ **Quantitative evidence**: Provides numerical validation metrics
- ✅ **Expected in journal**: Comparison plots are standard in validation papers

**Data Required**:
- MATLAB: `AvgFlowSetupDelay(ms)` from `metrics_comosat.txt`
- Mininet: Total latency from `emulation_metrics.json` (sum of components)

**Journal Placement**: Results section, after methodology

---

### Plot 2: Empirical Breakdown of Flow Setup Latency Components
**Title**: "Empirical Breakdown of Mean Flow Setup Latency Components"

**Purpose**: Validates individual cost model components

**Visualization**:
- **X-axis**: Time Slot (1 to 25)
- **Y-axis**: Latency (milliseconds, logarithmic scale)
- **Stacked bar chart** with three components:
  - **Green**: Propagation & Transmission Delay (base latency)
  - **Orange**: Controller Queuing Delay (δ_ab^que[t])
  - **Red**: Controller Processing Delay (CPU time)
- **Annotations**: Total latency values on top of bars (every 5th bar)

**Why Essential**:
- ✅ **Model component validation**: Validates each component of latency model
- ✅ **Empirical ground truth**: Real packet-level measurements
- ✅ **Research contribution**: Validates M/M/1 queuing assumption
- ✅ **Visual clarity**: Shows which component dominates in different scenarios

**Data Required**: From `emulation_metrics.json`:
- `prop_trans_delay`
- `queuing_delay`
- `processing_delay`

**Journal Placement**: Results section, alongside Plot 1

---

### Plot 3: Controller Remapping Overhead
**Title**: "Controller Remapping Statistics and Domain Evolution"

**Purpose**: Shows dynamic adaptation behavior

**Visualization**:
- **Two subplots**:
  1. **Top**: Remappings per time slot (line plot, blue)
  2. **Bottom**: Number of domains per time slot (line plot, green)
- **X-axis**: Time Slot (1 to 25)
- **Y-axis**: Count
- **Annotations**: Highlight slots with remapping spikes

**Why Essential**:
- ✅ **Algorithm behavior**: Shows COMOSAT adaptation strategy
- ✅ **Dynamic nature**: Demonstrates time-varying topology
- ✅ **Cost analysis**: Remapping overhead correlates with reconfiguration cost
- ✅ **Standard metric**: Common in controller placement papers

**Data Required**: From `simulation_metrics.json`:
- `remappings` per slot
- `num_domains` per slot

**Journal Placement**: Results section, performance analysis

---

## 📊 Priority 2: High-Value Plots (Strongly Recommended)

### Plot 4: Controller CPU Load vs. Adaptation Events
**Title**: "Controller CPU Load Correlation with Dynamic Adaptation Events"

**Purpose**: Validates reconfiguration overhead model

**Visualization**:
- **Dual-axis plot**:
  - **Left Y-axis**: Event Count (stacked bars)
    - Blue: Switch Handovers (low-cost)
    - Purple: Full Re-clustering (high-cost)
    - Red: GA Re-execution (high-cost)
  - **Right Y-axis**: CPU Utilization (%) (line plot, orange)
- **X-axis**: Time Slot (1 to 25)
- **Vertical lines**: Highlight slots with high-cost events

**Why High Value**:
- ✅ **Resource validation**: Connects algorithmic decisions to CPU usage
- ✅ **Hypothesis testing**: Validates that high-cost events cause CPU spikes
- ✅ **Empirical evidence**: Real resource measurements
- ✅ **Unique contribution**: Mininet-specific validation

**Data Required**: From `emulation_metrics.json`:
- `switch_handovers`, `full_reclustering`, `ga_reexecution`
- `cpu_utilization`

**Journal Placement**: Results section, resource analysis

---

### Plot 5: Network Topology Evolution (Selected Time Slots)
**Title**: "SAGIN Network Topology Evolution Across Time Slots"

**Purpose**: Visual demonstration of dynamic topology and controller placement

**Visualization**:
- **2×2 subplot grid** showing topology at slots: 1, 8, 15, 22
- **Geographic map** (lat/lon coordinates):
  - Colored nodes by domain (different colors)
  - Controllers marked with ★ (stars)
  - Node types: MEO (▲), LEO (■), Ground (●), HAPS (◆)
- **Legend**: Domain colors, node types, controller marker

**Why High Value**:
- ✅ **Visual clarity**: Shows spatial distribution
- ✅ **Controller placement**: Visualizes hierarchical structure
- ✅ **Dynamic nature**: Shows topology changes over time
- ✅ **Standard in papers**: Topology visualization is common

**Data Required**: From `topology/mininet_topology_data.json`:
- Node positions (latitude, longitude)
- Domain assignments
- Controller assignments

**Journal Placement**: Introduction or methodology section (to explain system)

---

### Plot 6: Queuing Delay vs. Arrival Rate
**Title**: "Controller Queuing Delay vs. PACKET-IN Arrival Rate"

**Purpose**: Validates M/M/1 queuing model assumption

**Visualization**:
- **Scatter plot**:
  - **X-axis**: Arrival Rate (packets/second)
  - **Y-axis**: Mean Queuing Delay (milliseconds)
  - **Points**: Each point is a time slot (colored by slot number)
- **Trend line**: M/M/1 theoretical curve (dashed line)
  - Formula: δ = λ / (μ(μ - λ)) where μ = service rate
- **Colorbar**: Sequential colormap showing time slot progression

**Why High Value**:
- ✅ **Model validation**: Tests queuing theory assumption
- ✅ **Theoretical fit**: Shows if empirical data matches M/M/1 model
- ✅ **Research rigor**: Validates modeling assumptions

**Data Required**: From `emulation_metrics.json`:
- `queuing_delay` per slot
- PACKET-IN arrival rate (needs to be calculated/collected)

**Journal Placement**: Results section, model validation subsection

---

## 📊 Priority 3: Supplementary Plots (If Space Permits)

### Plot 7: Controller Placement Evolution
**Title**: "Controller Placement Evolution Across Time Slots"

**Visualization**:
- **Timeline plot** showing:
  - Controller locations (nodes) at each slot
  - Lines connecting controller changes
  - Domain boundaries (colored regions)
- **Or**: **Heatmap** showing controller assignment changes

**Why Optional**:
- ✅ Provides detailed view of controller dynamics
- ⚠️ May be redundant if Plot 5 is included
- ⚠️ Can be complex to visualize clearly

---

### Plot 8: Processing Delay vs. Network Size
**Title**: "Controller Processing Delay vs. Domain Size"

**Purpose**: Validates computational complexity model

**Visualization**:
- **Scatter plot**:
  - **X-axis**: Number of Nodes in Domain (log scale)
  - **Y-axis**: Mean Processing Delay (milliseconds, log scale)
  - **Points**: Each point is a flow setup event
- **Trend line**: O(n²) or O(n log n) fitted curve

**Why Optional**:
- ✅ Validates computational complexity
- ⚠️ Requires detailed per-flow data
- ⚠️ May be too technical for main paper (could be in appendix)

---

### Plot 9: Cumulative Remapping Cost
**Title**: "Cumulative Remapping Overhead Over Time"

**Visualization**:
- **Line plot**:
  - **X-axis**: Time Slot
  - **Y-axis**: Cumulative Remapping Count
  - **Different lines**: Different algorithms (COMOSAT vs. KMPP vs. MCD)

**Why Optional**:
- ✅ Shows algorithm comparison
- ⚠️ Requires data from other algorithms
- ⚠️ May be better as a table

---

## 📋 Recommended Plot Configuration

### For Main Paper (6-8 plots):

1. **Plot 1**: MATLAB vs. Mininet Comparison ⭐⭐⭐
2. **Plot 2**: Latency Component Breakdown ⭐⭐⭐
3. **Plot 3**: Remapping Statistics ⭐⭐⭐
4. **Plot 4**: CPU vs. Adaptation Events ⭐⭐
5. **Plot 5**: Topology Evolution (4 slots) ⭐⭐
6. **Plot 6**: Queuing Delay vs. Arrival Rate ⭐⭐

### For Supplementary Material (Optional):

- Plot 7: Detailed Controller Evolution
- Plot 8: Processing Delay vs. Network Size
- Plot 9: Algorithm Comparison

---

## 🎨 Plot Design Guidelines

### Color Scheme (Recommended)
- **Primary colors**: Blue (#3498db), Red (#e74c3c), Green (#2ecc71)
- **Secondary colors**: Orange (#f39c12), Purple (#9b59b6)
- **Consistent palette**: Use same colors across all plots
- **Accessibility**: Ensure colorblind-friendly palette

### Figure Quality
- **Resolution**: 300 DPI minimum for publication
- **Format**: PDF or PNG (vector for line plots, raster for complex plots)
- **Size**: Single column: 85mm width, Double column: 170mm width
- **Font size**: 10pt minimum, readable at publication size

### Labels and Annotations
- **Clear axis labels**: Include units (ms, %, packets/sec)
- **Legend**: Position outside plot area, clear and concise
- **Annotations**: Mark significant events (reconfigurations, spikes)
- **Grid**: Light grid for readability

---

## 📊 Data Collection Priority

### High Priority (Must Collect)
1. ✅ Total flow setup latency (from MATLAB and Mininet)
2. ✅ Latency components (propagation, queuing, processing)
3. ✅ Remapping counts per slot
4. ✅ Domain counts per slot
5. ✅ CPU utilization per slot

### Medium Priority (Strongly Recommended)
6. ⚠️ Adaptation event counts (handovers, reclustering, GA)
7. ⚠️ PACKET-IN arrival rates
8. ⚠️ Network topology snapshots

### Low Priority (Nice to Have)
9. ⚪ Processing delay vs. domain size
10. ⚪ Per-flow latency data

---

## 📝 Journal Paper Structure Integration

### Abstract
- Mention: "Empirical validation using Mininet/Ryu emulation"
- Highlight: "Validates MATLAB cost models with real SDN measurements"

### Introduction
- **Plot 5**: Topology visualization (to explain system)

### Methodology
- **Plot 5**: Topology visualization (if not in introduction)
- Mention: Emulation setup, data collection methods

### Results
- **Plot 1**: MATLAB vs. Mininet comparison (main validation)
- **Plot 2**: Latency component breakdown (detailed validation)
- **Plot 3**: Remapping statistics (algorithm behavior)
- **Plot 4**: CPU vs. adaptation events (resource validation)
- **Plot 6**: Queuing delay validation (model assumption validation)

### Discussion
- Reference plots: Analyze what they show
- Compare: MATLAB predictions vs. empirical results
- Explain: Discrepancies and their causes

### Conclusion
- Summarize: Validation results from plots
- Highlight: Key findings from empirical measurements

---

## ✅ Checklist Before Submission

- [ ] All plots have clear titles and axis labels
- [ ] Colors are consistent across all figures
- [ ] Resolution is 300+ DPI
- [ ] Fonts are readable at publication size
- [ ] Legends are clear and positioned appropriately
- [ ] Error bars or confidence intervals shown (if applicable)
- [ ] Statistical significance noted (if applicable)
- [ ] All plots are referenced in text
- [ ] Captions are descriptive and informative
- [ ] Data sources are documented

---

## 🎯 Final Recommendations

**For a strong journal paper, include:**

1. **Plot 1** (MATLAB vs. Mininet) - **Essential**
2. **Plot 2** (Latency Breakdown) - **Essential**
3. **Plot 3** (Remapping Statistics) - **Essential**
4. **Plot 4** (CPU vs. Events) - **Strongly Recommended**
5. **Plot 5** (Topology Evolution) - **Strongly Recommended**
6. **Plot 6** (Queuing Validation) - **Recommended**

**Total: 6 plots** (appropriate for a journal paper)

This provides:
- ✅ Comprehensive validation of MATLAB models
- ✅ Empirical evidence from Mininet/Ryu
- ✅ Visual demonstration of system dynamics
- ✅ Model assumption validation
- ✅ Resource usage validation

These plots will make a strong contribution to your journal paper by demonstrating both theoretical modeling and empirical validation.

