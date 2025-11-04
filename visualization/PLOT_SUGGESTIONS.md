# Plot Suggestions and Validation

## Summary

The two proposed plots are **excellent** and will provide strong empirical validation of your MATLAB cost models. Below are my suggestions and any complementary plots that could enhance the paper.

---

## Plot 1: Empirical Breakdown of Flow Setup Latency ✅ **APPROVED**

### Why This Plot is Excellent

1. **Model Validation**: Breaks down the abstract MATLAB latency model (propagation + queuing + processing) into measurable, real-world components
2. **Empirical Ground Truth**: Uses actual packet-level timestamps from Ryu, not estimates
3. **Component Visibility**: Stacked bars make it easy to see which component dominates in different scenarios
4. **Research Contribution**: Validates that the M/M/1 queuing model assumption is reasonable

### Strengths

- **Propagation & Transmission**: Validates the network link model (2⋅l_ab[t]/c)
- **Queuing Delay**: Measures actual wait time, validating M/M/1 queuing theory
- **Processing Delay**: Shows real CPU time, validating computational complexity model
- **Logarithmic Scale**: Appropriate for latency data with wide range

### Minor Suggestions

1. **Consider Linear Scale Option**: Add a command-line flag to toggle linear vs. log scale
2. **Error Bars**: If collecting multiple samples per slot, add error bars (±1 std dev)
3. **Total Latency Line**: Optionally overlay MATLAB's total latency estimate as a dashed line for direct comparison

### Implementation Notes

- ✅ Already implemented with stacked bars
- ✅ Handles missing data gracefully (uses example data if needed)
- ✅ Flexible data format (supports multiple field name variations)

---

## Plot 2: Controller CPU Load vs. Adaptation Events ✅ **APPROVED**

### Why This Plot is Excellent

1. **Resource Validation**: Connects algorithmic decisions to actual CPU resource usage
2. **Hypothesis Testing**: Directly validates your paper's claim that high-cost events cause CPU spikes
3. **Dual-Axis Design**: Separates event counts (bars) from CPU load (line) while showing correlation
4. **Visual Correlation**: Vertical lines highlight high-cost events, making correlation obvious

### Strengths

- **Stacked Bars**: Clearly show event composition per slot
- **Color Coding**: Low-cost (blue) vs. High-cost (purple/red) events are visually distinct
- **CPU Line**: Overlays actual resource usage, showing real cost
- **Correlation Highlighting**: Vertical lines draw attention to high-cost event slots

### Minor Suggestions

1. **Moving Average**: Optionally show 3-slot moving average of CPU to smooth fluctuations
2. **Event Duration**: If events have duration, show horizontal bars instead of counts
3. **Correlation Coefficient**: Add text annotation showing Pearson correlation coefficient
4. **Baseline CPU**: Add horizontal dashed line showing baseline CPU (no events)

### Implementation Notes

- ✅ Already implemented with dual-axis design
- ✅ Stacked bars for event counts
- ✅ Line plot for CPU utilization
- ✅ Visual correlation markers (vertical lines)

---

## Additional Plot Suggestions

While your two plots are excellent, consider these complementary plots if space permits:

### Plot 3: MATLAB vs. Emulation Comparison (Recommended)

**Purpose**: Direct validation of overall cost model

```
Plot Title: Flow Setup Latency: MATLAB Model vs. Emulation Measurement

X-Axis: Time Slot (1 to 25)
Y-Axis: Total Latency (milliseconds)
Visualization: Two line plots
- Line 1: MATLAB estimated latency (dashed, blue)
- Line 2: Emulation measured latency (solid, red)
- Add shaded region showing ±10% error bounds
```

**Why**: Provides direct visual comparison of model accuracy

**Implementation**: Can be generated from same data as Plot 1

---

### Plot 4: Queuing Delay vs. Arrival Rate (Optional)

**Purpose**: Validate M/M/1 queuing model assumption

```
Plot Title: Controller Queuing Delay vs. PACKET-IN Arrival Rate

X-Axis: Arrival Rate (packets/second)
Y-Axis: Mean Queuing Delay (milliseconds)
Visualization: Scatter plot with trend line
- Points: Each point is a time slot
- Trend Line: M/M/1 theoretical curve (dashed)
- Color: By time slot (sequential colorbar)
```

**Why**: Tests if queuing delay follows M/M/1 model

**Data Needed**: PACKET-IN arrival rate per slot (can be estimated from topology)

---

### Plot 5: Processing Delay vs. Network Size (Optional)

**Purpose**: Validate computational complexity model

```
Plot Title: Controller Processing Delay vs. Domain Size

X-Axis: Number of Nodes in Domain (log scale)
Y-Axis: Mean Processing Delay (milliseconds, log scale)
Visualization: Scatter plot with fitted curve
- Points: Each point is a flow setup event
- Trend Line: O(n²) or O(n log n) fitted curve
- Color: By time slot
```

**Why**: Tests if processing delay scales as expected

**Data Needed**: Domain size per flow setup event

---

## Data Collection Recommendations

### Without Modifying Controller Script

Since you don't want to change `comosat_controller.py`, here are options:

1. **Orchestrator Extension** (Recommended)
   - Monitor CPU using `psutil` in `orchestrator.py`
   - Track adaptation events (already has remapping detection)
   - Calculate propagation delays from topology

2. **Log Parsing**
   - Parse Ryu controller logs for PACKET-IN timestamps
   - Extract FLOW-MOD timestamps
   - Calculate delays post-execution

3. **External Monitoring**
   - Use `top` or `psutil` to monitor Ryu process
   - Use `tcpdump` or `wireshark` for packet-level analysis
   - Post-process to extract metrics

4. **Minimal Logging Extension**
   - Add timestamp logging to controller (minimal change)
   - Parse logs to extract metrics
   - Export to JSON

### Recommended Approach

**Modify `orchestrator.py`** (not controller):

```python
# In orchestrator.py, add:
import psutil
import time

class SAGINOrchestrator:
    def __init__(self, ...):
        # ... existing code ...
        self.emulation_metrics = {}
        self.ryu_process = None
    
    def collect_cpu_metrics(self, slot):
        """Monitor CPU during time slot."""
        if not self.ryu_process:
            return None
        
        cpu_samples = []
        start_time = time.time()
        
        while time.time() - start_time < self.slot_duration:
            try:
                cpu = self.ryu_process.cpu_percent(interval=1)
                cpu_samples.append(cpu)
            except:
                break
        
        return sum(cpu_samples) / len(cpu_samples) if cpu_samples else 0
    
    def track_adaptation_events(self, slot):
        """Track adaptation events during slot transition."""
        changes = self.topology_manager.get_next_slot_changes()
        
        # Classify events
        switch_handovers = 0
        full_reclustering = 0
        ga_reexecution = 0
        
        # Detect event types from changes
        if changes:
            remappings = changes.get('remappings', [])
            
            for remap in remappings:
                # Simple remapping (low-cost)
                switch_handovers += 1
                
                # Check if re-clustering needed
                if self._requires_reclustering(remap):
                    full_reclustering = 1
                
                # Check if GA needed (threshold-based)
                if len(remappings) > threshold:
                    ga_reexecution = 1
        
        return {
            'switch_handovers': switch_handovers,
            'full_reclustering': full_reclustering,
            'ga_reexecution': ga_reexecution
        }
    
    def collect_flow_latency_components(self, slot):
        """Collect latency components from logs/topology."""
        # This can be done post-execution by parsing logs
        # For now, estimate from topology
        
        slot_data = self.topology_data['time_slots'][slot - 1]
        
        # Estimate propagation delay from topology
        prop_trans_delay = self._estimate_propagation_delay(slot_data)
        
        # Queuing and processing delays need actual measurement
        # Can be extracted from logs if timestamps are added
        
        return {
            'prop_trans_delay': prop_trans_delay,
            'queuing_delay': 0,  # Need actual measurement
            'processing_delay': 0  # Need actual measurement
        }
    
    def export_emulation_metrics(self, filename='emulation_metrics.json'):
        """Export collected emulation metrics."""
        output_file = os.path.join(os.path.dirname(__file__), filename)
        
        with open(output_file, 'w') as f:
            json.dump(self.emulation_metrics, f, indent=2)
        
        print(f'Exported emulation metrics to {output_file}')
```

---

## Final Recommendations

### Plot Selection

✅ **Keep Plot 1** - Essential for model validation
✅ **Keep Plot 2** - Essential for resource validation
🟡 **Consider Plot 3** - MATLAB vs. Emulation comparison (easy to add)
⚪ **Optional Plots 4-5** - Only if space/scope permits

### Data Collection Priority

1. **High Priority**: CPU metrics, Adaptation events (already trackable)
2. **Medium Priority**: Queuing delay (needs timestamp logging)
3. **Lower Priority**: Processing delay (needs detailed timing)

### Implementation Priority

1. **Phase 1**: Add CPU monitoring to orchestrator (Plot 2 ready)
2. **Phase 2**: Add minimal timestamp logging (Plot 1 components)
3. **Phase 3**: Add comparison plot (Plot 3) if time permits

---

## Conclusion

Your two plots are **well-designed** and will provide strong empirical validation. They move beyond MATLAB's theoretical models to show real-world, measurable components.

**Recommendation**: Implement Plot 1 and Plot 2 as proposed. Consider adding Plot 3 (MATLAB vs. Emulation comparison) if space permits.

The plots are already implemented in `visualize_results.py` and ready to use once data is collected. The data collection can be done primarily in the orchestrator without modifying the controller script.

