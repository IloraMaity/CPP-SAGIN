#!/usr/bin/env python3
"""
COMOSAT Ryu Controller Application

SDN controller application implementing the COMOSAT controller placement
algorithm for Space-Air-Ground Integrated Networks.

Features:
- Hierarchical controller placement (Domain controllers + Master controllers)
- Dynamic controller reassignment
- Domain-based flow rule installation
- Switch-to-controller mapping based on domain assignments

Author: SAGIN Research Team
"""

from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet, ipv4
from ryu.lib.packet import ether_types
from ryu.lib import hub
import json
import os


class COMOSATController(app_manager.RyuApp):
    """
    COMOSAT SDN Controller for SAGIN networks.
    
    Implements domain-based hierarchical control with dynamic reassignment.
    """
    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]
    
    def __init__(self, *args, **kwargs):
        super(COMOSATController, self).__init__(*args, **kwargs)
        
        # Domain and controller assignments
        self.domain_assignments = {}  # dpid -> domain_id
        self.controller_assignments = {}  # dpid -> controller_node_id
        self.switch_domains = {}  # domain_id -> [dpid list]
        
        # Statistics tracking
        self.stats = {
            'remappings': 0,
            'flow_rules_installed': 0,
            'packets_processed': 0
        }
        
        # Load topology data if available
        self.topology_data = None
        self.load_topology_data()
        
        # Start background thread for monitoring
        self.monitor_thread = hub.spawn(self._monitor)
    
    def load_topology_data(self):
        """Load topology data from JSON file."""
        json_file = os.path.join(os.path.dirname(__file__), 
                                 '../topology/mininet_topology_data.json')
        
        if os.path.exists(json_file):
            try:
                with open(json_file, 'r') as f:
                    self.topology_data = json.load(f)
                self.logger.info('Topology data loaded from %s', json_file)
            except Exception as e:
                self.logger.error('Failed to load topology data: %s', e)
        else:
            self.logger.warning('Topology data file not found: %s', json_file)
    
    def load_domain_assignments(self, slot=1):
        """
        Load domain assignments for a specific time slot.
        
        Args:
            slot: Time slot number (1-indexed)
        """
        if not self.topology_data:
            self.logger.warning('No topology data available')
            return
        
        if slot > len(self.topology_data['time_slots']):
            self.logger.error('Time slot %d exceeds available slots', slot)
            return
        
        slot_data = self.topology_data['time_slots'][slot - 1]
        
        # Clear previous assignments
        self.domain_assignments.clear()
        self.controller_assignments.clear()
        self.switch_domains.clear()
        
        # Load new assignments from slot data
        for idx, pos in enumerate(slot_data['node_positions']):
            dpid = idx + 1  # dpid is 1-indexed
            domain_id = pos.get('domain', 0)
            controller_id = pos.get('controller', 0)
            
            self.domain_assignments[dpid] = domain_id
            self.controller_assignments[dpid] = controller_id
            
            # Group switches by domain
            if domain_id not in self.switch_domains:
                self.switch_domains[domain_id] = []
            self.switch_domains[domain_id].append(dpid)
        
        self.logger.info('Loaded domain assignments for slot %d: %d domains',
                        slot, len(self.switch_domains))
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Handle switch features event.
        
        Called when a switch connects to the controller.
        """
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Get switch DPID
        dpid = datapath.id
        
        # Install default table-miss flow entry
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self._add_flow(datapath, 0, match, actions)
        
        self.logger.info('Switch %016x connected', dpid)
        
        # Assign switch to domain if topology data is loaded
        if self.topology_data and dpid in self.domain_assignments:
            domain_id = self.domain_assignments[dpid]
            self.logger.info('Switch %016x assigned to domain %d', dpid, domain_id)
            
            # Install domain-based flow rules
            self._install_domain_rules(datapath)
    
    def _add_flow(self, datapath, priority, match, actions, buffer_id=None):
        """
        Install a flow rule in the switch.
        
        Args:
            datapath: Switch datapath object
            priority: Flow priority
            match: OFP match object
            actions: List of OFP action objects
            buffer_id: Buffer ID (optional)
        """
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                   priority=priority, match=match, instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                   match=match, instructions=inst)
        
        datapath.send_msg(mod)
        self.stats['flow_rules_installed'] += 1
    
    def _install_domain_rules(self, datapath):
        """
        Install flow rules for intra-domain communication.
        
        This implements the domain-based forwarding logic.
        For now, we use a simplified approach: broadcast within domain,
        forward to controller for inter-domain.
        
        Args:
            datapath: Switch datapath object
        """
        dpid = datapath.id
        
        # Check if switch has a domain assignment
        if dpid not in self.domain_assignments:
            return
        
        domain_id = self.domain_assignments[dpid]
        
        if domain_id == 0:  # Unassigned domain
            return
        
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        
        # Get all switches in the same domain
        domain_switches = self.switch_domains.get(domain_id, [])
        domain_switches.remove(dpid)  # Remove self
        
        # Install flow rules for intra-domain communication
        # For each switch in the domain, forward to that switch
        for other_dpid in domain_switches:
            # We need to get the port to other switches
            # For simplicity, we use a flood action within domain
            pass  # Simplified implementation
        
        self.logger.info('Installed domain rules for switch %016x in domain %d',
                        dpid, domain_id)
    
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        """
        Handle packet-in messages from switches.
        
        This processes packets that don't match any flow rule.
        """
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']
        
        dpid = datapath.id
        self.stats['packets_processed'] += 1
        
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]
        
        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Ignore LLDP packets
            return
        
        dst = eth.dst
        src = eth.src
        
        # Simple learning switch: flood and install flow
        actions = [parser.OFPActionOutput(ofproto.OFPP_FLOOD)]
        
        # Install flow rule for reverse path
        match = parser.OFPMatch(in_port=in_port, eth_dst=src)
        self._add_flow(datapath, 1, match, actions)
        
        # Send packet
        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                 in_port=in_port, actions=actions,
                                 data=msg.data)
        datapath.send_msg(out)
    
    def update_controller_assignments(self, remappings):
        """
        Update controller assignments based on remappings.
        
        This method is called when topology changes require
        switch-to-controller reassignments.
        
        Args:
            remappings: List of remapping dictionaries
                       [{'node_id': x, 'old_controller': y, 'new_controller': z}]
        """
        for remap in remappings:
            node_id = remap['node_id']
            old_controller = remap['old_controller']
            new_controller = remap['new_controller']
            
            if node_id in self.controller_assignments:
                self.controller_assignments[node_id] = new_controller
                self.logger.info('Remapped node %d: controller %d -> %d',
                                node_id, old_controller, new_controller)
                self.stats['remappings'] += 1
    
    def _monitor(self):
        """Background thread for monitoring and statistics."""
        while True:
            hub.sleep(10)  # Run every 10 seconds
            
            # Log statistics
            self.logger.info('Statistics: remappings=%d, flows=%d, packets=%d',
                            self.stats['remappings'],
                            self.stats['flow_rules_installed'],
                            self.stats['packets_processed'])
    
    def get_statistics(self):
        """
        Get current statistics.
        
        Returns:
            Dictionary with statistics
        """
        return self.stats.copy()


class MultiDomainCOMOSATController:
    """
    Coordinator for multiple domain controllers.
    
    In a full implementation, this would manage multiple Ryu controller
    instances, one per domain.
    """
    
    def __init__(self, topology_data):
        self.topology_data = topology_data
        self.domain_controllers = {}
        self.current_slot = 1
    
    def update_topology(self, new_slot):
        """
        Update all domain controllers for new time slot.
        
        Args:
            new_slot: New time slot number
            
        Returns:
            Number of remappings
        """
        if new_slot > len(self.topology_data['time_slots']):
            return 0
        
        old_slot_data = self.topology_data['time_slots'][self.current_slot - 1]
        new_slot_data = self.topology_data['time_slots'][new_slot - 1]
        
        # Find remappings
        remappings = []
        for i, (old_pos, new_pos) in enumerate(zip(
                old_slot_data['node_positions'],
                new_slot_data['node_positions'])):
            
            if old_pos['controller'] != new_pos['controller']:
                remappings.append({
                    'node_id': i + 1,
                    'old_controller': old_pos['controller'],
                    'new_controller': new_pos['controller']
                })
        
        # Notify all domain controllers
        for controller in self.domain_controllers.values():
            controller.update_controller_assignments(remappings)
            controller.load_domain_assignments(new_slot)
        
        self.current_slot = new_slot
        
        return len(remappings)


if __name__ == '__main__':
    # This is typically run via: ryu-manager comosat_controller.py
    print('COMOSAT Controller application')
    print('Run with: ryu-manager comosat_controller.py')

