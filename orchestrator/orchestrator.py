#!/usr/bin/env python3
"""
SAGIN Network Orchestrator

Coordinates time slot transitions and dynamic topology updates for the
Mininet/Ryu COMOSAT implementation.

Features:
- Manages multiple time slots
- Triggers topology updates
- Collects performance metrics
- Coordinates controller reassignments
"""

import os
import sys
import time
import json
import subprocess
from threading import Thread
from mininet.net import Mininet
from mininet.log import setLogLevel, info, error
from mininet.node import OVSSwitch, Controller, RemoteController
from mininet.link import TCLink

# Add paths for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../topology'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../controller'))

from sagin_topology import SAGINTopology, DynamicTopologyManager, load_topology_data


class SAGINOrchestrator:
    """
    Main orchestrator for SAGIN network simulation.
    
    Manages the lifecycle of the Mininet network across multiple time slots,
    coordinating topology changes and controller reassignments.
    """
    
    def __init__(self, json_file='mininet_topology_data.json', num_slots=10, slot_duration=60,
                 remote_controller_ip=None, remote_controller_port=6633):
        """
        Initialize the orchestrator.
        
        Args:
            json_file: Path to topology JSON file
            num_slots: Number of time slots to simulate
            slot_duration: Duration of each time slot in seconds
            remote_controller_ip: IP address of remote Ryu controller (None for local)
            remote_controller_port: Port of remote Ryu controller (default: 6633)
        """
        self.topology_data = load_topology_data(json_file)
        self.topology_manager = DynamicTopologyManager(self.topology_data)
        self.num_slots = num_slots
        self.slot_duration = slot_duration
        
        self.net = None
        self.metrics = []
        self.current_slot = 1
        
        # Controller configuration
        self.remote_controller_ip = remote_controller_ip
        self.remote_controller_port = remote_controller_port
        self.use_remote = remote_controller_ip is not None
        
        # Ryu controller process (only for local controller)
        self.ryu_process = None
        
    def start_ryu_controller(self):
        """
        Start Ryu SDN controller in background.
        
        Returns:
            subprocess.Popen object for the controller process
        """
        info('Starting Ryu controller...\n')
        
        controller_script = os.path.join(
            os.path.dirname(__file__), 
            '../controller/comosat_controller.py'
        )
        
        if not os.path.exists(controller_script):
            error('Controller script not found: %s\n' % controller_script)
            return None
        
        try:
            # Start Ryu controller
            proc = subprocess.Popen(
                ['ryu-manager', '--verbose', controller_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            info('Ryu controller started (PID: %d)\n' % proc.pid)
            return proc
            
        except Exception as e:
            error('Failed to start Ryu controller: %s\n' % str(e))
            return None
    
    def stop_ryu_controller(self):
        """Stop the Ryu controller process."""
        if self.ryu_process:
            info('Stopping Ryu controller...\n')
            self.ryu_process.terminate()
            try:
                self.ryu_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.ryu_process.kill()
            self.ryu_process = None
    
    def setup_network(self, slot=1):
        """
        Set up Mininet network for a specific time slot.
        
        Args:
            slot: Time slot number (1-indexed)
        """
        info('Setting up network for time slot %d...\n' % slot)
        
        # Create topology
        topo = SAGINTopology(self.topology_data, current_slot=slot)
        
        # Select controller type based on configuration
        if self.use_remote:
            info('Using remote Ryu controller at %s:%d\n' % 
                 (self.remote_controller_ip, self.remote_controller_port))
            controller = RemoteController('ryu', 
                                         ip=self.remote_controller_ip,
                                         port=self.remote_controller_port)
        else:
            controller = Controller
        
        # Create network
        self.net = Mininet(
            topo=topo,
            controller=controller,
            switch=OVSSwitch,
            link=TCLink,  # Use TCLink for custom link parameters
            autoStaticArp=True
        )
        
        self.net.start()
        info('Network started successfully\n')
        
        # Verify connectivity
        self.verify_connectivity()
    
    def verify_connectivity(self):
        """
        Verify basic connectivity in the network.
        
        This is a simplified check - in full implementation,
        we would verify inter-domain and intra-domain connectivity.
        """
        info('Verifying connectivity...\n')
        
        hosts = self.net.hosts
        if len(hosts) < 2:
            info('Not enough hosts to test connectivity\n')
            return
        
        # Simple ping test
        h1 = hosts[0]
        h2 = hosts[1]
        
        result = h1.cmd('ping -c 1 %s' % h2.IP())
        if '1 received' in result:
            info('Connectivity verified between %s and %s\n' % (h1, h2))
        else:
            info('Connectivity check failed\n')
    
    def collect_metrics(self, slot):
        """
        Collect performance metrics for the current time slot.
        
        Args:
            slot: Current time slot number
            
        Returns:
            Dictionary with metrics
        """
        metrics = {
            'slot': slot,
            'timestamp': time.time(),
            'num_nodes': len(self.net.switches),
            'num_domains': 0,
            'remappings': 0
        }
        
        # Get slot data to count domains
        slot_data = self.topology_data['time_slots'][slot - 1]
        unique_domains = set()
        
        for pos in slot_data['node_positions']:
            domain = pos.get('domain', 0)
            if domain > 0:
                unique_domains.add(domain)
        
        metrics['num_domains'] = len(unique_domains)
        
        # Get remappings if not first slot
        if slot > 1:
            changes = self.topology_manager.get_next_slot_changes()
            if changes:
                metrics['remappings'] = len(changes.get('remappings', []))
        
        self.metrics.append(metrics)
        
        return metrics
    
    def transition_to_next_slot(self):
        """
        Transition to the next time slot.
        
        This simulates the dynamic topology changes as the network evolves.
        In a full implementation, this would update the network topology
        based on satellite movement.
        
        Returns:
            True if transition successful, False if no more slots
        """
        if self.current_slot >= self.num_slots:
            info('All time slots completed\n')
            return False
        
        next_slot = self.current_slot + 1
        info('\n--- Transitioning to Time Slot %d ---\n' % next_slot)
        
        # Get topology changes
        changes = self.topology_manager.get_next_slot_changes()
        
        if changes:
            num_remappings = len(changes.get('remappings', []))
            info('Detected %d controller remappings\n' % num_remappings)
            
            for remap in changes['remappings']:
                info('  Node %d: controller %d -> %d\n' % (
                    remap['node_id'],
                    remap['old_controller'],
                    remap['new_controller']
                ))
        
        # Note: Mininet doesn't support dynamic topology updates well
        # In a full implementation, we would:
        # 1. Update links based on satellite positions
        # 2. Reassign controllers
        # 3. Update flow rules
        
        # For now, we just collect metrics
        self.current_slot = next_slot
        
        return True
    
    def run_simulation(self):
        """
        Run the complete simulation across all time slots.
        
        This is the main simulation loop.
        """
        info('=== Starting SAGIN Network Simulation ===\n')
        
        # Start Ryu controller (only for local controller)
        if not self.use_remote:
            self.ryu_process = self.start_ryu_controller()
            time.sleep(2)  # Wait for controller to start
        else:
            info('Using remote controller, skipping local start\n')
        
        try:
            # Initialize network for first slot
            self.setup_network(slot=1)
            
            # Collect initial metrics
            self.collect_metrics(slot=1)
            
            # Simulate remaining time slots
            for slot in range(2, self.num_slots + 1):
                info('\nWaiting for slot duration (%d seconds)...\n' % self.slot_duration)
                time.sleep(self.slot_duration)
                
                # Transition to next slot
                if not self.transition_to_next_slot():
                    break
                
                # Collect metrics for this slot
                self.collect_metrics(slot=slot)
            
            info('\n=== Simulation Complete ===\n')
            
        except KeyboardInterrupt:
            info('\nSimulation interrupted by user\n')
            
        finally:
            # Clean up
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        info('Cleaning up resources...\n')
        
        if self.net:
            self.net.stop()
        
        self.stop_ryu_controller()
        
        info('Cleanup complete\n')
    
    def export_metrics(self, filename='simulation_metrics.json'):
        """
        Export collected metrics to JSON file.
        
        Args:
            filename: Output filename
        """
        # Try to write to results directory first (for Docker), fallback to orchestrator dir
        results_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'results')
        if os.path.exists(results_dir) and os.access(results_dir, os.W_OK):
            # Write to results directory (Docker environment)
            output_file = os.path.join(results_dir, filename)
        else:
            # Write to orchestrator directory (local environment)
            output_file = os.path.join(os.path.dirname(__file__), filename)
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(self.metrics, f, indent=2)
        
        info('Metrics exported to %s\n' % output_file)
        return output_file
    
    def print_summary(self):
        """Print simulation summary statistics."""
        info('\n=== Simulation Summary ===\n')
        
        if not self.metrics:
            info('No metrics collected\n')
            return
        
        total_remappings = sum(m.get('remappings', 0) for m in self.metrics)
        avg_domains = sum(m.get('num_domains', 0) for m in self.metrics) / len(self.metrics)
        
        info('Total time slots: %d\n' % len(self.metrics))
        info('Total remappings: %d\n' % total_remappings)
        info('Average domains per slot: %.2f\n' % avg_domains)
        info('Average remappings per slot: %.2f\n' % (total_remappings / len(self.metrics) if self.metrics else 0))
    
    def generate_visualizations(self, metrics_file=None):
        """
        Generate visualization plots after simulation.
        
        Args:
            metrics_file: Path to metrics JSON file (default: auto-detect)
        """
        try:
            # Import visualization module
            vis_module_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'visualization')
            if not os.path.exists(vis_module_path):
                info('Visualization module not found, skipping plot generation\n')
                return
            
            sys.path.insert(0, vis_module_path)
            from visualize_results import SAGINVisualizer
            
            # Determine paths
            base_dir = os.path.dirname(os.path.dirname(__file__))
            topology_file = os.path.join(base_dir, 'topology', 'mininet_topology_data.json')
            plots_dir = os.path.join(base_dir, 'plots')
            
            # Auto-detect metrics file
            if metrics_file is None:
                results_dir = os.path.join(base_dir, 'results')
                if os.path.exists(results_dir):
                    metrics_file = os.path.join(results_dir, 'simulation_metrics.json')
                else:
                    metrics_file = os.path.join(os.path.dirname(__file__), 'simulation_metrics.json')
            
            # Ensure plots directory exists
            os.makedirs(plots_dir, exist_ok=True)
            
            # Create visualizer
            if not os.path.exists(topology_file):
                info('Topology file not found, skipping visualization\n')
                return
            
            info('Generating visualizations...\n')
            visualizer = SAGINVisualizer(topology_file)
            
            # Generate plots
            metrics_path = metrics_file if os.path.isabs(metrics_file) else os.path.join(base_dir, metrics_file)
            visualizer.generate_report(
                metrics_file=metrics_path,
                output_dir=plots_dir,
                include_emulation_plots=False  # Skip emulation plots (need additional data)
            )
            
            info('Visualizations saved to %s\n' % plots_dir)
            
        except ImportError as e:
            info('Could not import visualization module: %s\n' % str(e))
            info('Skipping plot generation\n')
        except Exception as e:
            info('Error generating visualizations: %s\n' % str(e))
            info('Continuing without plots...\n')


def main():
    """
    Main entry point for the orchestrator.
    
    Can be run standalone or imported by other scripts.
    """
    import argparse
    
    parser = argparse.ArgumentParser(description='SAGIN Network Orchestrator')
    parser.add_argument('--json', type=str, default='mininet_topology_data.json',
                       help='Topology JSON file')
    parser.add_argument('--slots', type=int, default=10,
                       help='Number of time slots to simulate')
    parser.add_argument('--duration', type=int, default=60,
                       help='Duration of each time slot in seconds')
    parser.add_argument('--remote-controller-ip', type=str, default=None,
                       help='IP address of remote Ryu controller (use for separate VMs)')
    parser.add_argument('--remote-controller-port', type=int, default=6633,
                       help='Port of remote Ryu controller (default: 6633)')
    parser.add_argument('--generate-plots', action='store_true',
                       help='Generate visualization plots after simulation')
    
    args = parser.parse_args()
    
    setLogLevel('info')
    
    # Check if topology file exists
    json_path = os.path.join(os.path.dirname(__file__), '../topology', args.json)
    if not os.path.exists(json_path):
        error('Topology file not found: %s\n' % json_path)
        error('Please run the MATLAB export script first.\n')
        return
    
    # Create and run orchestrator
    orchestrator = SAGINOrchestrator(
        json_file=json_path,
        num_slots=args.slots,
        slot_duration=args.duration,
        remote_controller_ip=args.remote_controller_ip,
        remote_controller_port=args.remote_controller_port
    )
    
    try:
        orchestrator.run_simulation()
        metrics_file = orchestrator.export_metrics()
        orchestrator.print_summary()
        
        # Generate visualizations if requested
        if args.generate_plots:
            orchestrator.generate_visualizations(metrics_file)
        
    except Exception as e:
        error('Simulation error: %s\n' % str(e))
        raise


if __name__ == '__main__':
    main()

