% =========================================================================
% export_to_mininet.m
% =========================================================================
% MATLAB script to export simulation data from COMOSAT/KMPP simulation
% to JSON format for Mininet/Ryu implementation
%
% Usage: After running KMPP or other simulation, call:
%   export_to_mininet('KMPP', 10)
%
% This script:
% 1. Loads the saved workspace from scenario_sagin_cpp.mat
% 2. Loads N_history from workspace (assuming simulation just ran)
% 3. Extracts node positions, domain assignments, and controller info
% 4. Exports data to JSON format for Python Mininet implementation
% =========================================================================

function export_to_mininet(algorithm_type, num_slots, output_dir)
% EXPORT_TO_MININET Export simulation data to JSON for Mininet
% Inputs:
%   algorithm_type: 'KMPP', 'COMOSAT', 'MCD', or 'HDS' (for reference only)
%   num_slots: number of time slots to export (default: 10)
%   output_dir: output directory for JSON files (default: '../topology/')

%% Default parameters
if nargin < 1, algorithm_type = 'COMOSAT'; end
if nargin < 2, num_slots = 10; end
if nargin < 3, output_dir = '../topology/'; end

fprintf('=== Exporting Simulation Data for Mininet/Ryu ===\n');
fprintf('Algorithm: %s\n', algorithm_type);
fprintf('Time Slots: %d\n', num_slots);

% Import required variables from caller's workspace using evalin
required_vars = {'node', 'meo_nodes', 'leo_nodes', 'ground_nodes', 'haps_count', ...
                 'space_nodes', 'slotDur', 'start_time', 'position', 'N_history', ...
                 'N', 'gs', 'haps_locations', 'haps_altitude'};
missing_vars = {};
for i = 1:length(required_vars)
    try
        % Import variable from caller's workspace
        eval([required_vars{i} ' = evalin(''caller'', ''' required_vars{i} ''');']);
        fprintf('  Imported: %s\n', required_vars{i});
    catch ME
        fprintf('  Failed to import: %s (%s)\n', required_vars{i}, ME.message);
        missing_vars{end+1} = required_vars{i};
    end
end

% Check for optional COMOSAT-specific variables
try
    x = evalin('caller', 'x');
catch
    x = [];
end
try
    y = evalin('caller', 'y');
catch
    y = [];
end
try
    adj = evalin('caller', 'adj');
catch
    adj = [];
end
try
    r = evalin('caller', 'r');
catch
    r = [];
end
try
    D = evalin('caller', 'D');
catch
    D = [];
end

if ~isempty(missing_vars)
    error('Missing required variables: %s\nPlease run the simulation first.', ...
        strjoin(missing_vars, ', '));
end

%% Check for COMOSAT-specific variables (x, y matrices)
is_comosat = strcmpi(algorithm_type, 'COMOSAT');
if is_comosat && isempty(x)
    warning('x matrix not found. If you need hierarchical controller info, re-run CPPsatEnhanced.');
    is_comosat = false;
end

%% Verify N_history exists and has sufficient slots
if isempty(N_history) || length(N_history) < num_slots
    if length(N_history) < num_slots
        warning('Only %d time slots available, reducing to %d slots', ...
            length(N_history), length(N_history));
        num_slots = length(N_history);
    else
        error('N_history is empty. Please run the simulation first.');
    end
end

%% Prepare export data structure
fprintf('\n--- Preparing Export Data ---\n');
export_data = struct();

% Time slot information
export_data.total_slots = num_slots;
export_data.slot_duration = slotDur; % in seconds
export_data.start_time = char(start_time);

% Debug: Check if variables exist in this scope
fprintf('Checking variable access: node=%d, meo_nodes=%d\n', node, meo_nodes);

% Extract node information
fprintf('Extracting node information...\n');
nodes_struct = struct();
nodes_struct.meo = [];
nodes_struct.leo = [];
nodes_struct.ground = [];
nodes_struct.haps = [];

% Extract MEO nodes
for i = 1:meo_nodes
    node_info = struct();
    node_info.id = i;
    node_info.name = char(N(i).name);
    node_info.type = 'SN_MEO';
    nodes_struct.meo = [nodes_struct.meo; node_info];
end

% Extract LEO nodes
for i = meo_nodes+1:space_nodes
    node_info = struct();
    node_info.id = i;
    node_info.name = char(N(i).name);
    node_info.type = 'SN_LEO';
    nodes_struct.leo = [nodes_struct.leo; node_info];
end

% Extract Ground nodes
for i = space_nodes+1:space_nodes+ground_nodes
    node_info = struct();
    node_info.id = i;
    node_info.name = char(N(i).name);
    node_info.type = 'TN_GRO';
    % Ground stations have lat/lon
    if exist('gs', 'var') && ~isempty(gs)
        gs_idx = i - space_nodes;
        if gs_idx <= size(gs, 1)
            node_info.latitude = gs(gs_idx).Latitude;
            node_info.longitude = gs(gs_idx).Longitude;
        end
    end
    nodes_struct.ground = [nodes_struct.ground; node_info];
end

% Extract HAPS nodes
for i = space_nodes+ground_nodes+1:node
    node_info = struct();
    node_info.id = i;
    node_info.name = char(N(i).name);
    node_info.type = 'AN_HAPS';
    % HAPS have lat/lon/alt
    if exist('haps_locations', 'var') && ~isempty(haps_locations)
        haps_idx = i - (space_nodes + ground_nodes);
        if haps_idx <= size(haps_locations, 1)
            node_info.latitude = haps_locations(haps_idx, 1);
            node_info.longitude = haps_locations(haps_idx, 2);
            if exist('haps_altitude', 'var')
                node_info.altitude = haps_altitude;
            end
        end
    end
    nodes_struct.haps = [nodes_struct.haps; node_info];
end

fprintf('  Extracted %d nodes total (MEO: %d, LEO: %d, Ground: %d, HAPS: %d)\n', ...
    node, length(nodes_struct.meo), length(nodes_struct.leo), ...
    length(nodes_struct.ground), length(nodes_struct.haps));

export_data.nodes = nodes_struct;

% Extract time slot data
fprintf('Extracting time slot data...\n');
export_data.time_slots = cell(num_slots, 1);
for slot_num = 1:num_slots
    fprintf('  Processing slot %d/%d...\n', slot_num, num_slots);
    
    slot_data = struct();
    slot_data.slot = slot_num;
    
    % Get N structure for this slot
    if slot_num <= length(N_history)
        N_slot = N_history{slot_num};
    else
        error('Time slot %d not found in N_history', slot_num);
    end
    
    % Extract node positions
    node_positions = [];
    wgs84 = wgs84Ellipsoid('meter');
    
    for i = 1:node
        pos = struct();
        
        % Get node type
        if isfield(N_slot(i), 'type')
            pos.type = char(N_slot(i).type);
        else
            pos.type = 'UNKNOWN';
        end
        
        % Get ECEF position for satellites (from position array)
        if i <= size(position, 3) && slot_num <= size(position, 2)
            pos.x = position(1, slot_num, i);
            pos.y = position(2, slot_num, i);
            pos.z = position(3, slot_num, i);
        else
            % Ground/HAPS nodes - will use lat/lon from node info
            pos.x = 0;
            pos.y = 0;
            pos.z = 0;
        end
        
        % Convert ECEF to lat/lon for easier visualization
        if pos.x ~= 0 || pos.y ~= 0 || pos.z ~= 0
            [lat, lon, alt] = ecef2geodetic(wgs84, pos.x, pos.y, pos.z);
            pos.latitude = lat;
            pos.longitude = lon;
            pos.altitude = alt;
        elseif strcmp(pos.type, 'TN_GRO') && exist('gs', 'var')
            % Ground stations
            gs_idx = i - space_nodes;
            if gs_idx > 0 && gs_idx <= size(gs, 1)
                pos.latitude = gs(gs_idx).Latitude;
                pos.longitude = gs(gs_idx).Longitude;
                pos.altitude = 0;
            end
        elseif strcmp(pos.type, 'AN_HAPS') && exist('haps_locations', 'var')
            % HAPS
            haps_idx = i - (space_nodes + ground_nodes);
            if haps_idx > 0 && haps_idx <= size(haps_locations, 1)
                pos.latitude = haps_locations(haps_idx, 1);
                pos.longitude = haps_locations(haps_idx, 2);
                if exist('haps_altitude', 'var')
                    pos.altitude = haps_altitude;
                else
                    pos.altitude = 20000;
                end
            end
        else
            pos.latitude = 0;
            pos.longitude = 0;
            pos.altitude = 0;
        end
        
        % Get domain assignment
        if isfield(N_slot(i), 'domain')
            pos.domain = N_slot(i).domain;
        else
            pos.domain = 0;
        end
        
        % Get controller assignment
        if isfield(N_slot(i), 'con')
            pos.controller = N_slot(i).con;
        else
            pos.controller = 0;
        end
        
        node_positions = [node_positions; pos];
    end
    slot_data.node_positions = node_positions;
    
    % Extract domain information
    unique_domains = unique([node_positions.domain]);
    unique_domains = unique_domains(unique_domains > 0); % Remove domain 0
    
    domain_list = [];
    for d = unique_domains'
        domain = struct();
        domain.id = d;
        
        % Find all nodes in this domain
        domain_nodes = [];
        domain_controller = 0;
        for i = 1:node
            if node_positions(i).domain == d
                domain_nodes = [domain_nodes; i];
                % Check if this node is the controller
                if node_positions(i).controller == i && domain_controller == 0
                    domain_controller = i;
                end
            end
        end
        domain.nodes = domain_nodes;
        domain.controller = domain_controller;
        domain_list = [domain_list; domain];
    end
    slot_data.domains = domain_list;
    
    fprintf('    Slot %d: %d nodes, %d domains\n', slot_num, node, length(unique_domains));
    
    export_data.time_slots{slot_num} = slot_data;
end

%% Export to JSON
output_file = fullfile(output_dir, 'mininet_topology_data.json');
fprintf('\n--- Exporting to JSON ---\n');
fprintf('Output file: %s\n', output_file);

% Create output directory if it doesn't exist
if ~exist(output_dir, 'dir')
    mkdir(output_dir);
end

% Convert MATLAB struct to JSON-compatible format
json_data = jsonencode(export_data, 'ConvertInfAndNaN', false);

% Write JSON file
fid = fopen(output_file, 'w');
if fid == -1
    error('Cannot open output file for writing: %s', output_file);
end

fprintf(fid, '%s', json_data);
fclose(fid);

fprintf('Export complete!\n');
fprintf('JSON file written to: %s\n', output_file);

end
