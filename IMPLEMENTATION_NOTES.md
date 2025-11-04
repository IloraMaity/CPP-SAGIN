# Implementation Notes

## Overview

This document provides additional implementation details and notes for the Mininet/Ryu COMOSAT implementation.

## Key Design Decisions

### 1. Data Format

The JSON topology format is structured as follows:

```json
{
  "total_slots": 10,
  "slot_duration": 900,
  "start_time": "...",
  "nodes": {
    "meo": [{"id": 1, "name": "...", "type": "SN_MEO"}],
    "leo": [{"id": 21, "name": "...", "type": "SN_LEO"}],
    "ground": [{"id": 41, "name": "...", "type": "TN_GRO", "latitude": ..., "longitude": ...}],
    "haps": [{"id": 61, "name": "...", "type": "AN_HAPS", "latitude": ..., "longitude": ..., "altitude": ...}]
  },
  "time_slots": [
    {
      "slot": 1,
      "node_positions": [{"type": "...", "x": ..., "y": ..., "z": ..., "latitude": ..., "longitude": ..., "altitude": ..., "domain": ..., "controller": ...}],
      "domains": [...]
    }
  ]
}
```

### 2. Node ID Mapping

**Important**: Node IDs are 1-indexed in the JSON data (MATLAB convention).
The Mininet topology uses these IDs directly for switch naming (s1, s2, ...).

When accessing `node_positions` array, remember it's 0-indexed:
- `node_positions[0]` → Node ID 1
- `node_positions[node_id - 1]` → Node with ID `node_id`

### 3. Domain Assignments

Each time slot contains:
- `node_positions`: Array of position data with domain and controller assignments
- `domains`: List of domain information (currently structured differently than expected)

The domain assignment logic extracts unique domains from `node_positions`, not from `domains`.

### 4. Controller Reassignment

Remappings are detected by comparing `controller` field across consecutive time slots:
- A remapping occurs when `controller[t] != controller[t-1]` for the same node
- Remap count excludes nodes with `controller == 0` (unassigned)

### 5. Link Modeling

**Current Implementation**: Simplified domain-based mesh
- Nodes within the same domain are connected
- Links have fixed 100ms delay and 100 Mbps bandwidth
- No inter-domain links

**Future Enhancement**: Full adjacency-based linking
- Parse adjacency matrix from MATLAB simulation
- Compute realistic delays from distance calculations
- Support dynamic link establishment/teardown

### 6. Controller Architecture

**Current**: Single Ryu controller instance
- All switches connect to one controller
- Domain-based flow rule installation

**Full Implementation**: Multi-controller setup
- One Ryu controller instance per domain
- Inter-controller communication for routing
- Hierarchical master controller coordination

### 7. Topology Updates

Mininet doesn't easily support dynamic topology changes once built.

**Current Workaround**: 
- Collect remapping statistics
- Log topology changes
- Rebuild topology if needed (not implemented)

**Full Solution**: Use link modification commands
- `ovs-ofctl mod-port` to disable/enable links
- Update flow tables dynamically
- Maintain adjacency mapping

## Known Limitations

### MATLAB Export

1. **HAPS/Ground Station Positions**: 
   - ECEF coordinates not always available in position array
   - Falls back to lat/lon from node data structure
   - May cause inconsistencies

2. **Domain Structure**:
   - MATLAB exports domains as list, not dict
   - Parser expects specific structure
   - May need adjustment for different algorithm outputs

3. **Link Data Missing**:
   - Adjacency matrix not exported
   - Link delays not exported
   - Requires manual calculation or estimation

### Mininet Topology

1. **Static Topology**:
   - Built once at initialization
   - No easy way to add/remove nodes dynamically
   - Link changes require reconfiguration

2. **Limited Realism**:
   - No radio propagation model
   - Fixed link characteristics
   - No packet loss, jitter, or bandwidth variations

3. **Scale Limitations**:
   - Tested with ~60 nodes
   - May not scale well to hundreds of nodes
   - Performance depends on host resources

### Ryu Controller

1. **Simplified Flow Rules**:
   - Basic learning switch behavior
   - No sophisticated routing algorithms
   - No QoS or traffic engineering

2. **No Inter-Controller Communication**:
   - Single controller instance
   - No coordination between domain controllers
   - No global network view

3. **Limited Statistics**:
   - Basic packet counters
   - No latency measurements
   - No flow-level statistics

### Visualization

1. **Basemap Dependency**:
   - Requires geospatial plotting library
   - May not work in headless environments
   - Fallback needed for missing package

2. **Limited Metrics**:
   - Only remapping count and domain count
   - No latency or throughput plots
   - No controller load visualization

3. **Static Plots**:
   - No real-time monitoring
   - No interactive visualization
   - Requires regenerating plots

## Testing Strategy

### Unit Testing
- Test JSON parsing
- Verify node ID mapping
- Check domain assignment logic
- Validate remapping detection

### Integration Testing
1. **MATLAB → JSON**:
   - Verify all data exported correctly
   - Check coordinate transformations
   - Validate domain structures

2. **JSON → Mininet**:
   - Create topology successfully
   - Verify all switches created
   - Check link establishment

3. **Mininet → Ryu**:
   - Controller connects to switches
   - Flow rules installed correctly
   - Packets forwarded properly

4. **End-to-End**:
   - Run full simulation
   - Collect metrics
   - Generate visualizations

### Test Scenarios

1. **Single Slot Test**: Verify basic topology creation
2. **Multi-Slot Test**: Validate remapping detection
3. **Domain Isolation Test**: Ensure traffic stays within domains
4. **Controller Handoff Test**: Measure remapping overhead
5. **Scalability Test**: Test with varying node counts

## Performance Considerations

### Computational Complexity
- **JSON Parsing**: O(N) where N = number of nodes
- **Topology Creation**: O(N²) for mesh connections
- **Remapping Detection**: O(N) per time slot
- **Visualization**: O(N×S) where S = number of slots

### Memory Usage
- Topology data: ~100 KB per time slot
- Mininet objects: ~1 MB per switch
- Visualization: ~5 MB per plot

### Execution Time
- MATLAB export: 1-5 seconds
- Mininet startup: 10-30 seconds (60 nodes)
- Simulation: N × slot_duration seconds
- Visualization: 10-30 seconds per plot

## Future Enhancements

### Short-Term
1. Export adjacency matrix from MATLAB
2. Implement realistic link delays
3. Add inter-domain routing
4. Support multiple controller instances
5. Add more visualization options

### Medium-Term
1. Continuous mobility simulation
2. Radio propagation modeling
3. Traffic generation and measurement
4. Q-learning for controller placement
5. Distributed controller coordination

### Long-Term
1. Real satellite network integration
2. Multi-layer network support
3. Edge computing integration
4. 5G/6G integration
5. Cloud deployment

## Troubleshooting Guide

### Common Issues

1. **MATLAB Export Fails**
   - Check `N_history` exists in workspace
   - Verify all required variables loaded
   - Check file paths and permissions

2. **Mininet Won't Start**
   - Check `sudo` permissions on Linux
   - Verify OpenVSwitch installed
   - Check `/dev/net/tun` device exists

3. **Ryu Controller Crashes**
   - Check Python version compatibility
   - Verify OpenFlow version matches
   - Check controller script paths

4. **Visualization Fails**
   - Install basemap: `conda install -c conda-forge basemap`
   - Check matplotlib backend
   - Verify data file exists

5. **Performance Issues**
   - Reduce number of time slots
   - Simplify topology
   - Disable unnecessary logging

## Code Organization

### Separation of Concerns
- **MATLAB**: Simulation and data generation
- **Mininet**: Network emulation
- **Ryu**: SDN control logic
- **Orchestrator**: Coordination and metrics
- **Visualization**: Result presentation

### Dependencies
```
MATLAB Export → JSON
             ↓
JSON → Mininet Topology → Ryu Controller
             ↓                ↓
        Orchestrator → Visualization
             ↓
        Metrics + Plots
```

### Configuration
All configuration should be centralized in:
- `experiments/run_experiment.sh` (Linux) or `.bat` (Windows)
- Can be overridden via command-line arguments

## References

### Related Work
- COMOSAT Algorithm: Reference paper
- Mininet Documentation: http://mininet.org
- Ryu Controller: http://ryu-sdn.org
- OpenFlow Specification: https://opennetworking.org

### Tools Used
- MATLAB R2020b+ with Aerospace Toolbox
- Python 3.8+ with packages as specified
- Mininet 2.3.0+
- Ryu SDN Framework 4.34+

## Contact

For questions or issues related to this implementation:
- Check README.md for general guidance
- Review this document for technical details
- Contact research team for advanced support

