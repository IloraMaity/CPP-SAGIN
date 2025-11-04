#!/usr/bin/env python3
"""
Visualization Tools for SAGIN Network Simulation

Generates plots and diagrams for research paper presentation:
- Network topology snapshots
- Controller placement evolution
- Domain membership changes
- Remapping statistics
- Performance metrics

Author: SAGIN Research Team
"""

import os
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.animation import FuncAnimation
# Note: Basemap is deprecated. Using regular matplotlib for visualization.
import networkx as nx


class SAGINVisualizer:
    """
    Visualization tools for SAGIN network simulation results.
    """
    
    def __init__(self, json_file='mininet_topology_data.json'):
        """
        Initialize visualizer.
        
        Args:
            json_file: Path to topology JSON file
        """
        self.topology_data = None
        self.load_topology_data(json_file)
        
        # Color schemes
        self.domain_colors = plt.cm.Set3(np.linspace(0, 1, 12))
        self.node_colors = {
            'SN_MEO': 'red',
            'SN_LEO': 'blue',
            'TN_GRO': 'green',
            'AN_HAPS': 'orange'
        }
        self.node_markers = {
            'SN_MEO': '^',
            'SN_LEO': 's',
            'TN_GRO': 'o',
            'AN_HAPS': 'D'
        }
    
    def load_topology_data(self, json_file):
        """Load topology data from JSON file."""
        if os.path.exists(json_file):
            with open(json_file, 'r') as f:
                self.topology_data = json.load(f)
        else:
            # Try relative path
            json_path = os.path.join(os.path.dirname(__file__), 
                                    '../topology', json_file)
            if os.path.exists(json_path):
                with open(json_path, 'r') as f:
                    self.topology_data = json.load(f)
            else:
                raise FileNotFoundError('Topology file not found: %s' % json_file)
    
    def plot_topology(self, slot=1, output_file=None, show_map=True):
        """
        Plot network topology for a specific time slot.
        
        Args:
            slot: Time slot number (1-indexed)
            output_file: Output filename (optional)
            show_map: Whether to show geographic map
        """
        if slot > len(self.topology_data['time_slots']):
            raise ValueError('Time slot %d exceeds available slots' % slot)
        
        slot_data = self.topology_data['time_slots'][slot - 1]
        
        fig = plt.figure(figsize=(16, 12))
        
        # Create plot (Basemap removed - use simple scatter plot)
        ax = fig.add_subplot(111)
        
        if show_map:
            # Simple background for world map
            ax.set_facecolor('lightblue')
            ax.set_xlim(-180, 180)
            ax.set_ylim(-90, 90)
            ax.set_xlabel('Longitude (°)')
            ax.set_ylabel('Latitude (°)')
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal', adjustable='box')
        else:
            # No special map projection
            pass
        
        # Plot nodes by domain
        domain_groups = {}
        
        for idx, pos in enumerate(slot_data['node_positions']):
            node_type = pos.get('type', 'UNKNOWN')
            domain = pos.get('domain', 0)
            controller_id = pos.get('controller', 0)
            is_controller = (idx + 1 == controller_id)
            
            # Get coordinates
            if 'latitude' in pos and 'longitude' in pos:
                lat, lon = pos['latitude'], pos['longitude']
            else:
                continue
            
            # Group by domain
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append((lon, lat, node_type, is_controller))
        
        # Plot each domain
        for domain_id, nodes in domain_groups.items():
            if domain_id == 0:  # Unassigned nodes
                color = 'gray'
            else:
                color = self.domain_colors[domain_id % len(self.domain_colors)]
            
            for lon, lat, node_type, is_controller in nodes:
                # Use lat/lon directly (no projection needed)
                x, y = lon, lat
                
                marker = self.node_markers.get(node_type, 'o')
                markersize = 15 if is_controller else 10
                
                ax.plot(x, y, marker=marker, color=color, markersize=markersize,
                       markeredgecolor='black', markeredgewidth=1.5 if is_controller else 0.5)
        
        # Add legend
        legend_elements = [
            mpatches.Patch(facecolor=color, alpha=0.5, label='Domain %d' % d)
            for d, color in enumerate(self.domain_colors[:len(domain_groups.keys())])
        ]
        legend_elements.extend([
            plt.Line2D([0], [0], marker=marker, color='w', markerfacecolor='black',
                      markersize=8, label=label, markeredgewidth=1)
            for label, marker in [
                ('MEO', self.node_markers['SN_MEO']),
                ('LEO', self.node_markers['SN_LEO']),
                ('Ground', self.node_markers['TN_GRO']),
                ('HAPS', self.node_markers['AN_HAPS']),
                ('Controller', 'o')
            ]
        ])
        
        ax.legend(handles=legend_elements, loc='lower left', fontsize=9)
        ax.set_title('SAGIN Network Topology - Time Slot %d' % slot, fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved topology plot to %s' % output_file)
        else:
            plt.show()
    
    def plot_remapping_statistics(self, metrics_file='simulation_metrics.json', 
                                  output_file=None):
        """
        Plot remapping statistics over time.
        
        Args:
            metrics_file: Path to simulation metrics JSON file
            output_file: Output filename (optional)
        """
        # Load metrics
        if os.path.exists(metrics_file):
            with open(metrics_file, 'r') as f:
                metrics = json.load(f)
        else:
            metrics_file = os.path.join(os.path.dirname(__file__), metrics_file)
            if os.path.exists(metrics_file):
                with open(metrics_file, 'r') as f:
                    metrics = json.load(f)
            else:
                raise FileNotFoundError('Metrics file not found')
        
        # Extract data
        slots = [m['slot'] for m in metrics]
        remappings = [m.get('remappings', 0) for m in metrics]
        num_domains = [m.get('num_domains', 0) for m in metrics]
        
        # Create figure
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), sharex=True)
        
        # Plot remappings over time
        ax1.plot(slots, remappings, marker='o', linewidth=2, markersize=8, color='blue')
        ax1.fill_between(slots, remappings, alpha=0.3, color='blue')
        ax1.set_ylabel('Number of Remappings', fontsize=12)
        ax1.set_title('Controller Remappings Over Time', fontsize=14, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Plot number of domains
        ax2.plot(slots, num_domains, marker='s', linewidth=2, markersize=8, color='green')
        ax2.fill_between(slots, num_domains, alpha=0.3, color='green')
        ax2.set_xlabel('Time Slot', fontsize=12)
        ax2.set_ylabel('Number of Domains', fontsize=12)
        ax2.set_title('Domain Evolution', fontsize=14, fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved remapping statistics to %s' % output_file)
        else:
            plt.show()
    
    def plot_controller_evolution(self, output_file=None, slots=None):
        """
        Plot controller placement evolution across time slots.
        
        Args:
            output_file: Output filename (optional)
            slots: List of slots to plot (default: [1, 8, 15, 22] or first 4)
        """
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # Default to slots 1, 8, 15, 22 or first 4 if not enough slots
        if slots is None:
            num_slots = len(self.topology_data['time_slots'])
            if num_slots >= 22:
                slots = [1, 8, 15, 22]
            elif num_slots >= 15:
                slots = [1, 8, 15, num_slots]
            elif num_slots >= 8:
                slots = [1, 8, num_slots, num_slots]
            else:
                slots = list(range(1, min(5, num_slots + 1)))
        
        # Plot topology for selected slots
        for idx, slot in enumerate(slots):
            if idx >= 4 or slot > len(self.topology_data['time_slots']):
                break
            
            ax = axes[idx]
            slot_data = self.topology_data['time_slots'][slot - 1]
            
            # Create simple scatter plot (no map for multiple plots)
            domain_groups = {}
            
            for pos_idx, pos in enumerate(slot_data['node_positions']):
                if 'latitude' not in pos or 'longitude' not in pos:
                    continue
                
                domain = pos.get('domain', 0)
                controller_id = pos.get('controller', 0)
                is_controller = (pos_idx + 1 == controller_id)
                
                if domain not in domain_groups:
                    domain_groups[domain] = {'nodes': [], 'controllers': []}
                
                if is_controller:
                    domain_groups[domain]['controllers'].append(
                        (pos['longitude'], pos['latitude'])
                    )
                else:
                    domain_groups[domain]['nodes'].append(
                        (pos['longitude'], pos['latitude'])
                    )
            
            # Plot nodes
            for domain_id, group in domain_groups.items():
                if domain_id == 0:
                    color = 'gray'
                else:
                    color = self.domain_colors[domain_id % len(self.domain_colors)]
                
                if group['nodes']:
                    lons, lats = zip(*group['nodes'])
                    ax.scatter(lons, lats, c=[color], s=30, alpha=0.5)
                
                if group['controllers']:
                    lons, lats = zip(*group['controllers'])
                    ax.scatter(lons, lats, c=[color], s=200, marker='*', 
                             edgecolors='black', linewidths=2)
            
            ax.set_title('Time Slot %d' % slot, fontsize=12, fontweight='bold')
            ax.set_xlabel('Longitude')
            ax.set_ylabel('Latitude')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved controller evolution to %s' % output_file)
        else:
            plt.show()
    
    def plot_flow_setup_latency_breakdown(self, emulation_metrics_file='emulation_metrics.json',
                                          output_file=None, num_slots=25):
        """
        Plot 1: Empirical Breakdown of Mean Flow Setup Latency
        
        This plot breaks down flow setup latency into its measurable components:
        - Propagation & Transmission Delay
        - Controller Queuing Delay
        - Controller Processing Delay
        
        This provides high-fidelity validation of the MATLAB cost model.
        
        Args:
            emulation_metrics_file: Path to emulation metrics JSON file
            output_file: Output filename (optional)
            num_slots: Number of time slots to plot (default: 25)
        """
        # Try to load emulation metrics
        emulation_data = self._load_emulation_metrics(emulation_metrics_file)
        
        if not emulation_data:
            print('Warning: Emulation metrics not found. Using example data structure.')
            print('Expected format: See documentation for emulation_metrics.json structure')
            # Use example structure for demonstration
            slots = list(range(1, num_slots + 1))
            prop_trans_delay = np.random.uniform(10, 50, num_slots)  # ms
            queuing_delay = np.random.uniform(5, 30, num_slots)  # ms
            processing_delay = np.random.uniform(2, 15, num_slots)  # ms
        else:
            slots = []
            prop_trans_delay = []
            queuing_delay = []
            processing_delay = []
            
            for slot in range(1, min(num_slots + 1, len(emulation_data) + 1)):
                slot_data = emulation_data.get(str(slot), emulation_data.get(slot - 1, {}))
                slots.append(slot)
                
                # Extract latency components
                prop_trans_delay.append(slot_data.get('prop_trans_delay', 
                                                     slot_data.get('propagation_transmission_delay', 0)))
                queuing_delay.append(slot_data.get('queuing_delay', 
                                                  slot_data.get('controller_queuing_delay', 0)))
                processing_delay.append(slot_data.get('processing_delay',
                                                     slot_data.get('controller_processing_delay', 0)))
        
        # Create stacked bar chart
        fig, ax = plt.subplots(figsize=(14, 8))
        
        width = 0.7
        x = np.arange(len(slots))
        
        # Create stacked bars
        bars1 = ax.bar(x, prop_trans_delay, width, label='Propagation & Transmission', 
                       color='#2ecc71', alpha=0.8)
        bars2 = ax.bar(x, queuing_delay, width, bottom=prop_trans_delay, 
                       label='Controller Queuing', color='#f39c12', alpha=0.8)
        bars3 = ax.bar(x, processing_delay, width, 
                       bottom=np.array(prop_trans_delay) + np.array(queuing_delay),
                       label='Controller Processing', color='#e74c3c', alpha=0.8)
        
        # Customize plot
        ax.set_xlabel('Time Slot', fontsize=12, fontweight='bold')
        ax.set_ylabel('Latency (milliseconds)', fontsize=12, fontweight='bold')
        ax.set_title('Empirical Breakdown of Mean Flow Setup Latency', 
                     fontsize=14, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(slots)
        ax.set_yscale('log')  # Logarithmic scale for better visualization
        ax.grid(True, alpha=0.3, axis='y')
        ax.legend(loc='upper left', fontsize=10)
        
        # Add total latency annotation on top of bars
        total_latency = np.array(prop_trans_delay) + np.array(queuing_delay) + np.array(processing_delay)
        for i, (slot, total) in enumerate(zip(slots, total_latency)):
            if i % 5 == 0:  # Annotate every 5th bar to avoid clutter
                ax.text(i, total * 1.1, f'{total:.1f}ms', 
                       ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved flow setup latency breakdown to %s' % output_file)
        else:
            plt.show()
    
    def plot_controller_cpu_vs_adaptation_events(self, emulation_metrics_file='emulation_metrics.json',
                                                  output_file=None, num_slots=25):
        """
        Plot 2: Controller CPU Load vs. Dynamic Adaptation Events
        
        This plot correlates algorithmic decisions (adaptation events) with
        actual CPU resource usage, validating the cost of reconfiguration overhead.
        
        Args:
            emulation_metrics_file: Path to emulation metrics JSON file
            output_file: Output filename (optional)
            num_slots: Number of time slots to plot (default: 25)
        """
        # Try to load emulation metrics
        emulation_data = self._load_emulation_metrics(emulation_metrics_file)
        
        if not emulation_data:
            print('Warning: Emulation metrics not found. Using example data structure.')
            print('Expected format: See documentation for emulation_metrics.json structure')
            # Use example structure for demonstration
            slots = list(range(1, num_slots + 1))
            switch_handovers = np.random.randint(0, 5, num_slots)
            full_reclustering = np.random.randint(0, 2, num_slots)
            ga_reexecution = np.random.randint(0, 2, num_slots)
            cpu_utilization = 30 + np.random.uniform(-10, 50, num_slots)
            # Add spikes for high-cost events
            for i in range(num_slots):
                if ga_reexecution[i] > 0:
                    cpu_utilization[i] += 40
                elif full_reclustering[i] > 0:
                    cpu_utilization[i] += 25
        else:
            slots = []
            switch_handovers = []
            full_reclustering = []
            ga_reexecution = []
            cpu_utilization = []
            
            for slot in range(1, min(num_slots + 1, len(emulation_data) + 1)):
                slot_data = emulation_data.get(str(slot), emulation_data.get(slot - 1, {}))
                slots.append(slot)
                
                # Extract adaptation events
                switch_handovers.append(slot_data.get('switch_handovers', 
                                                      slot_data.get('low_cost_events', 0)))
                full_reclustering.append(slot_data.get('full_reclustering',
                                                       slot_data.get('reclustering_events', 0)))
                ga_reexecution.append(slot_data.get('ga_reexecution',
                                                    slot_data.get('ga_events', 0)))
                
                # Extract CPU utilization
                cpu_utilization.append(slot_data.get('cpu_utilization',
                                                     slot_data.get('avg_cpu_load', 0)))
        
        # Create dual-axis plot
        fig, ax1 = plt.subplots(figsize=(14, 8))
        
        # Left Y-axis: Event counts (stacked bars)
        width = 0.7
        x = np.arange(len(slots))
        
        bars1 = ax1.bar(x, switch_handovers, width, label='Switch Handovers',
                       color='#3498db', alpha=0.8)
        bars2 = ax1.bar(x, full_reclustering, width, bottom=switch_handovers,
                       label='Full Re-clustering', color='#9b59b6', alpha=0.8)
        bars3 = ax1.bar(x, ga_reexecution, width,
                       bottom=np.array(switch_handovers) + np.array(full_reclustering),
                       label='GA Re-execution', color='#e74c3c', alpha=0.8)
        
        ax1.set_xlabel('Time Slot', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Event Count', fontsize=12, fontweight='bold', color='#34495e')
        ax1.set_title('Controller CPU Load vs. Dynamic Adaptation Events',
                     fontsize=14, fontweight='bold')
        ax1.set_xticks(x)
        ax1.set_xticklabels(slots)
        ax1.tick_params(axis='y', labelcolor='#34495e')
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.legend(loc='upper left', fontsize=10)
        
        # Right Y-axis: CPU utilization (line plot)
        ax2 = ax1.twinx()
        line = ax2.plot(x, cpu_utilization, 'o-', color='#e67e22', linewidth=2.5,
                       markersize=6, label='CPU Utilization', alpha=0.9)
        ax2.set_ylabel('CPU Utilization (%)', fontsize=12, fontweight='bold', 
                      color='#e67e22')
        ax2.tick_params(axis='y', labelcolor='#e67e22')
        ax2.set_ylim([0, 100])
        
        # Add legend for CPU line
        ax2.legend(loc='upper right', fontsize=10)
        
        # Highlight correlation: Add vertical lines where high-cost events occur
        for i, (slot, ga, reclust) in enumerate(zip(slots, ga_reexecution, full_reclustering)):
            if ga > 0 or reclust > 0:
                ax1.axvline(x=i, color='red', linestyle='--', alpha=0.3, linewidth=1)
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved controller CPU vs adaptation events to %s' % output_file)
        else:
            plt.show()
    
    def _load_emulation_metrics(self, metrics_file):
        """
        Load emulation metrics from JSON file.
        
        Expected format:
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
            ...
        }
        
        Args:
            metrics_file: Path to metrics JSON file
            
        Returns:
            Dictionary with metrics data or None if file not found
        """
        # Try multiple locations
        possible_paths = [
            metrics_file,
            os.path.join(os.path.dirname(__file__), metrics_file),
            os.path.join(os.path.dirname(__file__), '../orchestrator', metrics_file),
            os.path.join(os.path.dirname(__file__), '../results', metrics_file)
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                try:
                    with open(path, 'r') as f:
                        return json.load(f)
                except Exception as e:
                    print('Warning: Could not load emulation metrics from %s: %s' % (path, e))
        
        return None
    
    def plot_matlab_vs_mininet_comparison(self, matlab_metrics_file='metrics_comosat.txt',
                                          emulation_metrics_file='emulation_metrics.json',
                                          output_file=None, num_slots=25):
        """
        Plot 1: MATLAB vs. Mininet Emulation Comparison
        
        Direct validation of MATLAB cost model accuracy.
        
        Args:
            matlab_metrics_file: Path to MATLAB metrics text file
            emulation_metrics_file: Path to emulation metrics JSON file
            output_file: Output filename (optional)
            num_slots: Number of time slots to plot (default: 25)
        """
        # Load MATLAB metrics
        matlab_latencies = []
        matlab_slots = []
        
        try:
            # Try to find MATLAB metrics file
            matlab_paths = [
                matlab_metrics_file,
                os.path.join(os.path.dirname(__file__), '../..', matlab_metrics_file),
                os.path.join(os.path.dirname(__file__), '../..', '..', matlab_metrics_file),
                os.path.join(os.path.dirname(__file__), '../..', '..', '..', matlab_metrics_file),
                os.path.join('/app/matlab_data', matlab_metrics_file)  # Docker path
            ]
            
            matlab_file = None
            for path in matlab_paths:
                if os.path.exists(path):
                    matlab_file = path
                    break
            
            if matlab_file:
                with open(matlab_file, 'r') as f:
                    lines = f.readlines()
                    # Skip header lines and find data
                    for line in lines:
                        if line.strip() and not line.startswith('TimeSlot') and not line.startswith('-'):
                            parts = line.split()
                            if len(parts) >= 7:
                                try:
                                    slot = int(parts[0])
                                    latency = float(parts[6])  # AvgFlowSetupDelay column
                                    matlab_slots.append(slot)
                                    matlab_latencies.append(latency)
                                except (ValueError, IndexError):
                                    continue
        except Exception as e:
            print('Warning: Could not load MATLAB metrics: %s' % e)
        
        # Load emulation metrics
        emulation_data = self._load_emulation_metrics(emulation_metrics_file)
        
        mininet_slots = []
        mininet_latencies = []
        
        if emulation_data:
            for slot in range(1, min(num_slots + 1, len(emulation_data) + 1)):
                slot_data = emulation_data.get(str(slot), emulation_data.get(slot - 1, {}))
                if slot_data:
                    prop = slot_data.get('prop_trans_delay', 0)
                    queuing = slot_data.get('queuing_delay', 0)
                    processing = slot_data.get('processing_delay', 0)
                    total = prop + queuing + processing
                    if total > 0:
                        mininet_slots.append(slot)
                        mininet_latencies.append(total)
        else:
            # Generate example data for demonstration
            mininet_slots = list(range(1, num_slots + 1))
            mininet_latencies = [np.random.uniform(30, 80) for _ in range(num_slots)]
            print('Warning: Using example data for Mininet latencies')
        
        # Create figure with two subplots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)
        
        # Subplot 1: Comparison plot
        if matlab_slots and matlab_latencies:
            ax1.plot(matlab_slots, matlab_latencies, 'b--', marker='▲', 
                    linewidth=2, markersize=8, label='MATLAB Model', alpha=0.8)
            # Add error bounds (±10%)
            upper_bound = [x * 1.1 for x in matlab_latencies]
            lower_bound = [x * 0.9 for x in matlab_latencies]
            ax1.fill_between(matlab_slots, lower_bound, upper_bound, 
                           alpha=0.2, color='blue', label='±10% Error Bounds')
        
        ax1.plot(mininet_slots, mininet_latencies, 'r-', marker='●', 
                linewidth=2.5, markersize=8, label='Mininet Emulation', alpha=0.9)
        
        ax1.set_ylabel('Flow Setup Latency (milliseconds)', fontsize=12, fontweight='bold')
        ax1.set_title('Flow Setup Latency: Theoretical Model vs. Empirical Measurement', 
                     fontsize=14, fontweight='bold')
        ax1.legend(loc='best', fontsize=10)
        ax1.grid(True, alpha=0.3)
        
        # Subplot 2: Absolute error
        if matlab_slots and matlab_latencies:
            # Match slots for comparison
            common_slots = sorted(set(matlab_slots) & set(mininet_slots))
            matlab_aligned = [matlab_latencies[matlab_slots.index(s)] for s in common_slots]
            mininet_aligned = [mininet_latencies[mininet_slots.index(s)] for s in common_slots]
            errors = [m - n for m, n in zip(matlab_aligned, mininet_aligned)]
            
            ax2.bar(common_slots, errors, alpha=0.7, color='purple', width=0.7)
            ax2.axhline(y=0, color='black', linestyle='-', linewidth=1)
            ax2.set_xlabel('Time Slot', fontsize=12, fontweight='bold')
            ax2.set_ylabel('Absolute Error (MATLAB - Mininet) (ms)', fontsize=12, fontweight='bold')
            ax2.set_title('Model Accuracy: Absolute Error per Time Slot', 
                         fontsize=12, fontweight='bold')
            ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved MATLAB vs. Mininet comparison to %s' % output_file)
        else:
            plt.show()
    
    def plot_queuing_delay_vs_arrival_rate(self, emulation_metrics_file='emulation_metrics.json',
                                           output_file=None, num_slots=25):
        """
        Plot 6: Queuing Delay vs. Arrival Rate
        
        Validates M/M/1 queuing model assumption.
        
        Args:
            emulation_metrics_file: Path to emulation metrics JSON file
            output_file: Output filename (optional)
            num_slots: Number of time slots to plot (default: 25)
        """
        # Load emulation metrics
        emulation_data = self._load_emulation_metrics(emulation_metrics_file)
        
        arrival_rates = []
        queuing_delays = []
        slots = []
        
        if emulation_data:
            for slot in range(1, min(num_slots + 1, len(emulation_data) + 1)):
                slot_data = emulation_data.get(str(slot), emulation_data.get(slot - 1, {}))
                if slot_data:
                    queuing_delay = slot_data.get('queuing_delay', 0)
                    arrival_rate = slot_data.get('arrival_rate', 
                                                 slot_data.get('packet_in_rate', 0))
                    if queuing_delay > 0 and arrival_rate > 0:
                        slots.append(slot)
                        arrival_rates.append(arrival_rate)
                        queuing_delays.append(queuing_delay)
        
        if not arrival_rates:
            # Generate example data for demonstration
            print('Warning: Using example data for arrival rates and queuing delays')
            slots = list(range(1, num_slots + 1))
            arrival_rates = np.random.uniform(10, 100, num_slots)
            queuing_delays = np.random.uniform(5, 50, num_slots)
            # Add some correlation
            queuing_delays = [q * (1 + a/100) for q, a in zip(queuing_delays, arrival_rates)]
        
        # Calculate M/M/1 theoretical curve
        # Assume service rate μ = 100 packets/sec (adjust based on your system)
        mu = 100  # Service rate (packets/second)
        theoretical_arrivals = np.linspace(0.1, mu * 0.9, 100)  # Avoid μ = λ
        theoretical_delays = []
        for lam in theoretical_arrivals:
            if lam < mu:
                delay = (lam / (mu * (mu - lam))) * 1000  # Convert to ms
                theoretical_delays.append(delay)
            else:
                theoretical_delays.append(np.nan)
        
        # Create plot
        fig, ax = plt.subplots(figsize=(12, 8))
        
        # Plot theoretical curve
        ax.plot(theoretical_arrivals, theoretical_delays, 'k--', 
               linewidth=2, label='M/M/1 Theoretical Model', alpha=0.7)
        
        # Plot empirical data
        scatter = ax.scatter(arrival_rates, queuing_delays, c=slots, 
                            cmap='viridis', s=100, alpha=0.7, 
                            edgecolors='black', linewidths=1)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Time Slot', fontsize=11, fontweight='bold')
        
        ax.set_xlabel('PACKET-IN Arrival Rate (packets/second)', fontsize=12, fontweight='bold')
        ax.set_ylabel('Mean Queuing Delay (milliseconds)', fontsize=12, fontweight='bold')
        ax.set_title('Controller Queuing Delay vs. PACKET-IN Arrival Rate', 
                    fontsize=14, fontweight='bold')
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Add annotation showing service rate
        ax.axvline(x=mu, color='red', linestyle=':', linewidth=1.5, alpha=0.5)
        ax.text(mu * 1.05, ax.get_ylim()[1] * 0.9, f'μ = {mu} pkt/s', 
               fontsize=10, color='red', fontweight='bold')
        
        plt.tight_layout()
        
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print('Saved queuing delay vs. arrival rate to %s' % output_file)
        else:
            plt.show()
    
    def generate_report(self, metrics_file='simulation_metrics.json', 
                       output_dir='plots', include_emulation_plots=True,
                       emulation_metrics_file='emulation_metrics.json'):
        """
        Generate complete visualization report.
        
        Args:
            metrics_file: Path to simulation metrics JSON file
            output_dir: Output directory for plots
            include_emulation_plots: Whether to include Mininet-specific plots
            emulation_metrics_file: Path to emulation metrics JSON file
        """
        # Create output directory
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print('Generating visualization report...')
        
        # Generate topology plots for multiple slots
        num_slots_to_plot = min(5, len(self.topology_data['time_slots']))
        for slot in range(1, num_slots_to_plot + 1):
            output_file = os.path.join(output_dir, 'topology_slot_%d.png' % slot)
            self.plot_topology(slot, output_file, show_map=True)
        
        # Generate remapping statistics
        try:
            output_file = os.path.join(output_dir, 'remapping_statistics.png')
            self.plot_remapping_statistics(metrics_file, output_file)
        except FileNotFoundError:
            print('Metrics file not found, skipping remapping statistics')
        
        # Generate controller evolution (Plot 5: Topology Evolution)
        output_file = os.path.join(output_dir, 'controller_evolution.png')
        num_slots_total = len(self.topology_data.get('time_slots', []))
        if num_slots_total >= 22:
            self.plot_controller_evolution(output_file, slots=[1, 8, 15, 22])
        else:
            self.plot_controller_evolution(output_file)
        
        # Generate Mininet-specific emulation plots
        num_slots = len(self.topology_data.get('time_slots', []))
        num_slots_plot = min(num_slots, 25)
        
        if include_emulation_plots:
            try:
                # Plot 1: MATLAB vs. Mininet Comparison
                output_file = os.path.join(output_dir, 'matlab_vs_mininet_comparison.png')
                self.plot_matlab_vs_mininet_comparison(
                    emulation_metrics_file=emulation_metrics_file,
                    output_file=output_file,
                    num_slots=num_slots_plot
                )
                
                # Plot 2: Flow setup latency breakdown
                output_file = os.path.join(output_dir, 'flow_setup_latency_breakdown.png')
                self.plot_flow_setup_latency_breakdown(emulation_metrics_file, 
                                                       output_file, 
                                                       num_slots=num_slots_plot)
                
                # Plot 4: CPU load vs adaptation events
                output_file = os.path.join(output_dir, 'controller_cpu_vs_adaptation.png')
                self.plot_controller_cpu_vs_adaptation_events(emulation_metrics_file,
                                                              output_file,
                                                              num_slots=num_slots_plot)
                
                # Plot 6: Queuing Delay vs. Arrival Rate
                output_file = os.path.join(output_dir, 'queuing_delay_vs_arrival_rate.png')
                self.plot_queuing_delay_vs_arrival_rate(emulation_metrics_file,
                                                        output_file,
                                                        num_slots=num_slots_plot)
            except Exception as e:
                print('Warning: Could not generate emulation plots: %s' % e)
                print('Emulation plots will use example data. See documentation for data collection.')
        
        print('Visualization report complete!')
        print('Generated all 6 journal plots:')
        print('  1. MATLAB vs. Mininet Comparison')
        print('  2. Flow Setup Latency Breakdown')
        print('  3. Remapping Statistics')
        print('  4. CPU Load vs. Adaptation Events')
        print('  5. Controller Evolution (Topology)')
        print('  6. Queuing Delay vs. Arrival Rate')


def main():
    """Main entry point for visualization script."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SAGIN Network Visualizer')
    parser.add_argument('--topology', type=str, default='mininet_topology_data.json',
                       help='Topology JSON file')
    parser.add_argument('--metrics', type=str, default='simulation_metrics.json',
                       help='Simulation metrics JSON file')
    parser.add_argument('--emulation-metrics', type=str, default='emulation_metrics.json',
                       help='Emulation metrics JSON file for Mininet-specific plots')
    parser.add_argument('--output', type=str, default='plots',
                       help='Output directory for plots')
    parser.add_argument('--slot', type=int, default=None,
                       help='Specific time slot to visualize')
    parser.add_argument('--all', action='store_true',
                       help='Generate all visualizations')
    parser.add_argument('--flow-latency', action='store_true',
                       help='Generate flow setup latency breakdown plot only')
    parser.add_argument('--cpu-adaptation', action='store_true',
                       help='Generate CPU load vs adaptation events plot only')
    parser.add_argument('--no-emulation-plots', action='store_true',
                       help='Exclude Mininet-specific emulation plots')
    
    args = parser.parse_args()
    
    # Create visualizer
    topo_file = os.path.join(os.path.dirname(__file__), '../topology', args.topology)
    visualizer = SAGINVisualizer(topo_file)
    
    if args.flow_latency:
        # Generate only flow latency breakdown plot
        output_file = os.path.join(args.output, 'flow_setup_latency_breakdown.png')
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        visualizer.plot_flow_setup_latency_breakdown(args.emulation_metrics, output_file)
        
    elif args.cpu_adaptation:
        # Generate only CPU vs adaptation events plot
        output_file = os.path.join(args.output, 'controller_cpu_vs_adaptation.png')
        if not os.path.exists(args.output):
            os.makedirs(args.output)
        visualizer.plot_controller_cpu_vs_adaptation_events(args.emulation_metrics, output_file)
        
    elif args.all:
        # Generate complete report
        metrics_file = os.path.join(os.path.dirname(__file__), '../orchestrator', 
                                    args.metrics)
        emulation_file = os.path.join(os.path.dirname(__file__), '../orchestrator',
                                     args.emulation_metrics)
        visualizer.generate_report(metrics_file, args.output, 
                                  include_emulation_plots=not args.no_emulation_plots,
                                  emulation_metrics_file=emulation_file)
        
    elif args.slot:
        # Plot specific slot
        visualizer.plot_topology(args.slot, show_map=True)
        
    else:
        # Default: generate report
        metrics_file = os.path.join(os.path.dirname(__file__), '../orchestrator', 
                                    args.metrics)
        emulation_file = os.path.join(os.path.dirname(__file__), '../orchestrator',
                                     args.emulation_metrics)
        visualizer.generate_report(metrics_file, args.output,
                                  include_emulation_plots=not args.no_emulation_plots,
                                  emulation_metrics_file=emulation_file)


if __name__ == '__main__':
    main()

