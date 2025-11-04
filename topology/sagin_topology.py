#!/usr/bin/env python3
"""
SAGIN Topology Builder for Mininet/Ryu COMOSAT Implementation

This module creates a custom Mininet topology representing a Space-Air-Ground
Integrated Network (SAGIN) with dynamic topology changes based on simulation data
from the MATLAB COMOSAT/KMPP algorithm.

Author: SAGIN Research Team
"""

import json
import os
from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Controller, OVSSwitch
from mininet.link import TCLink
from mininet.log import setLogLevel, info


class SAGINTopology(Topo):
    """
    Custom Mininet topology class for SAGIN network simulation.
    
    Represents satellites (LEO/MEO), HAPS, and ground stations as switches,
    with dynamic topology changes based on time slots.
    """
    
    def __init__(self, topology_data, current_slot=1, **opts):
        """
        Initialize SAGIN topology from JSON data.
        
        Args:
            topology_data: Dictionary containing topology configuration
            current_slot: Current time slot (1-indexed)
            **opts: Additional topology options
        """
        Topo.__init__(self, **opts)
        
        self.topology_data = topology_data
        self.current_slot = current_slot
        self.nodes_dict = {}  # Maps node ID to mininet switch name
        self.domains = {}  # Domain information for current slot
        
        # Build topology
        self._build_topology()
    
    def _build_topology(self):
        """Build the network topology based on current time slot."""
        info('Building SAGIN topology for time slot %d...\n' % self.current_slot)
        
        # Get current slot data
        slot_data = self.topology_data['time_slots'][self.current_slot - 1]
        self.domains = slot_data
        
        # Create switches for each node
        for node_type in ['meo', 'leo', 'ground', 'haps']:
            if node_type not in self.topology_data['nodes']:
                continue
                
            nodes = self.topology_data['nodes'][node_type]
            for node in nodes:
                self._create_switch(node, node_type, slot_data)
        
        # Create links between nodes
        self._create_links(slot_data)
    
    def _create_switch(self, node_data, node_type, slot_data):
        """
        Create a switch for a network node.
        
        Args:
            node_data: Node information dictionary
            node_type: Type of node ('meo', 'leo', 'ground', 'haps')
            slot_data: Current time slot data
        """
        node_id = node_data['id']
        node_name = 's%d' % node_id
        
        # Find domain and controller for this node
        # Note: node_positions is a list of dictionaries without an 'id' field
        # We need to match by index in the node_positions array
        domain_id = 0
        controller_id = 0
        if node_id <= len(slot_data['node_positions']):
            pos = slot_data['node_positions'][node_id - 1]  # Convert to 0-indexed
            domain_id = pos.get('domain', 0)
            controller_id = pos.get('controller', 0)
        
        # Create switch with metadata
        metadata = {
            'node_id': node_id,
            'node_type': node_type,
            'domain': domain_id,
            'controller': controller_id,
            'display_name': node_data.get('name', node_name)  # Renamed to avoid conflict
        }
        
        # Add switch to topology
        self.addSwitch(node_name, **metadata)
        self.nodes_dict[node_id] = node_name
    
    def _create_links(self, slot_data):
        """
        Create links between nodes based on adjacency.
        
        For now, this creates a simplified topology. In the full implementation,
        this would use the adjacency matrix from the simulation.
        
        Args:
            slot_data: Current time slot data
        """
        # For demonstration: create links within domains only
        domain_groups = {}
        
        for idx, pos in enumerate(slot_data['node_positions']):
            domain = pos['domain']
            node_id = idx + 1  # Convert from 0-indexed to 1-indexed
            
            if domain not in domain_groups:
                domain_groups[domain] = []
            domain_groups[domain].append(node_id)
        
        # Create mesh within each domain
        for domain, nodes in domain_groups.items():
            if domain == 0:  # Skip unassigned nodes
                continue
                
            # Create links within domain (simplified: minimum spanning tree)
            if len(nodes) > 1:
                # Connect first node to all others
                first_node = nodes[0]
                if first_node not in self.nodes_dict:
                    continue
                    
                switch1 = self.nodes_dict[first_node]
                for other_node in nodes[1:]:
                    if other_node not in self.nodes_dict:
                        continue
                        
                    switch2 = self.nodes_dict[other_node]
                    # Add link with appropriate delay based on distance
                    delay = self._calculate_link_delay(slot_data, first_node, other_node)
                    
                    self.addLink(switch1, switch2, 
                                delay='%dms' % int(delay),
                                bw=100,  # 100 Mbps
                                loss=0)
    
    def _calculate_link_delay(self, slot_data, node1_id, node2_id):
        """
        Calculate link delay based on node positions.
        
        Args:
            slot_data: Current time slot data
            node1_id: First node ID
            node2_id: Second node ID
            
        Returns:
            Delay in milliseconds
        """
        # Simple delay calculation: 10-500ms based on approximate distance
        # In full implementation, this would use ECEF coordinates
        
        # Find nodes in slot data (using 1-indexed node IDs)
        pos1 = None
        pos2 = None
        
        if 1 <= node1_id <= len(slot_data['node_positions']):
            pos1 = slot_data['node_positions'][node1_id - 1]
        if 1 <= node2_id <= len(slot_data['node_positions']):
            pos2 = slot_data['node_positions'][node2_id - 1]
        
        if not pos1 or not pos2:
            return 100  # Default delay
        
        # Use geodetic coordinates if available
        if 'latitude' in pos1 and 'longitude' in pos1:
            # Approximate delay based on distance
            # For satellite networks, RTT is typically 50-300ms
            return 100  # Simplified: 100ms delay
        else:
            return 100  # Default
    
    def update_topology(self, new_slot):
        """
        Update topology for new time slot.
        
        Note: Mininet doesn't support dynamic topology updates easily.
        This method returns information needed for the orchestrator to
        rebuild the topology.
        
        Args:
            new_slot: New time slot number
            
        Returns:
            Dictionary with topology change information
        """
        if new_slot > len(self.topology_data['time_slots']):
            info('Warning: Time slot %d exceeds available slots\n' % new_slot)
            return None
        
        changes = {
            'remappings': [],
            'new_links': [],
            'removed_links': []
        }
        
        old_slot_data = self.topology_data['time_slots'][self.current_slot - 1]
        new_slot_data = self.topology_data['time_slots'][new_slot - 1]
        
        # Find controller remappings
        for i, (old_pos, new_pos) in enumerate(zip(
                old_slot_data['node_positions'],
                new_slot_data['node_positions'])):
            
            if old_pos['controller'] != new_pos['controller']:
                changes['remappings'].append({
                    'node_id': i + 1,  # Convert to 1-indexed
                    'old_controller': old_pos['controller'],
                    'new_controller': new_pos['controller']
                })
        
        self.current_slot = new_slot
        
        return changes


class DynamicTopologyManager:
    """
    Manages dynamic topology changes across time slots.
    
    This class coordinates topology updates and controller reassignments
    when transitioning between time slots.
    """
    
    def __init__(self, topology_data):
        """
        Initialize the dynamic topology manager.
        
        Args:
            topology_data: Full topology data from JSON
        """
        self.topology_data = topology_data
        self.current_slot = 1
        self.remap_count = 0
    
    def get_next_slot_changes(self):
        """
        Get topology changes for the next time slot.
        
        Returns:
            Dictionary with changes, or None if no more slots
        """
        if self.current_slot >= len(self.topology_data['time_slots']):
            return None
        
        next_slot = self.current_slot + 1
        
        old_slot = self.topology_data['time_slots'][self.current_slot - 1]
        new_slot = self.topology_data['time_slots'][next_slot - 1]
        
        changes = {
            'remappings': [],
            'new_links': [],
            'removed_links': []
        }
        
        # Count remappings
        for i, (old_pos, new_pos) in enumerate(zip(old_slot['node_positions'], 
                                                     new_slot['node_positions'])):
            if old_pos['controller'] != new_pos['controller'] and old_pos['controller'] != 0:
                changes['remappings'].append({
                    'node_id': i + 1,  # Convert to 1-indexed
                    'old_controller': old_pos['controller'],
                    'new_controller': new_pos['controller']
                })
        
        self.current_slot = next_slot
        return changes
    
    def get_remapping_count(self):
        """Get the number of remappings in current slot."""
        return self.remap_count


def load_topology_data(json_file):
    """
    Load topology data from JSON file.
    
    Args:
        json_file: Path to JSON topology file
        
    Returns:
        Dictionary with topology data
    """
    info('Loading topology data from %s...\n' % json_file)
    
    if not os.path.exists(json_file):
        raise FileNotFoundError('Topology file not found: %s' % json_file)
    
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    info('Loaded topology with %d time slots, %d nodes\n' % 
         (data['total_slots'], sum(len(data['nodes'][k]) for k in data['nodes'].keys())))
    
    return data


if __name__ == '__main__':
    # Test topology creation
    setLogLevel('info')
    
    # Check if topology data exists
    json_file = 'mininet_topology_data.json'
    if not os.path.exists(json_file):
        info('Topology data file not found: %s\n' % json_file)
        info('Please run the MATLAB export script first.\n')
        exit(1)
    
    # Load topology data
    topology_data = load_topology_data(json_file)
    
    # Create topology
    topo = SAGINTopology(topology_data, current_slot=1)
    
    info('Topology created successfully!\n')
    info('Nodes: %d\n' % len(topo.nodes_dict))
    info('Domains: %d\n' % len(topo.domains.get('domains', [])))

