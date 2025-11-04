% =========================================================================
% export_to_mininet_script.m
% =========================================================================
% SCRIPT version of export_to_mininet - can access base workspace variables
% =========================================================================

%% Default parameters
if ~exist('algorithm_type', 'var'), algorithm_type = 'COMOSAT'; end
if ~exist('num_slots', 'var'), num_slots = 10; end
if ~exist('output_dir', 'var'), output_dir = '../topology/'; end

fprintf('=== Exporting Simulation Data for Mininet/Ryu ===\n');
fprintf('Algorithm: %s\n', algorithm_type);
fprintf('Time Slots: %d\n', num_slots);

%% Check for required workspace variables
required_vars = {'node', 'meo_nodes', 'leo_nodes', 'ground_nodes', 'haps_count', ...
                 'space_nodes', 'slotDur', 'start_time', 'position', 'N_history'};
missing_vars = {};
for i = 1:length(required_vars)
    if ~exist(required_vars{i}, 'var')
        missing_vars{end+1} = required_vars{i};
    end
end

if ~isempty(missing_vars)
    error('Missing required variables: %s\nPlease run the simulation first.', ...
        strjoin(missing_vars, ', '));
end

%% Check for COMOSAT-specific variables (x, y matrices)
is_comosat = strcmpi(algorithm_type, 'COMOSAT');
if is_comosat && ~exist('x', 'var')
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

% Extract node information
fprintf('Extracting node information...\n');
export_data.nodes = extract_node_info();

% Extract time slot data
fprintf('Extracting time slot data...\n');
export_data.time_slots = cell(num_slots, 1);
for slot = 1:num_slots
    fprintf('  Processing slot %d/%d...\n', slot, num_slots);
    export_data.time_slots{slot} = extract_slot_data(slot);
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

%% Helper Functions

function nodes_struct = extract_node_info()
% Extract static node information from workspace variables

% Define node structure
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
        if gs_idx <= numel(gs) && isfield(gs(gs_idx), 'Latitude')
            node_info.latitude = gs(gs_idx).Latitude;
            node_info.longitude = gs(gs_idx).Longitude;
            node_info.altitude = 0;
        end
    end
    nodes_struct.ground = [nodes_struct.ground; node_info];
end

% Extract HAPS nodes
for i = space_nodes+ground_nodes+1:node
    node_info = struct();
    node_info.id = i;
    node_info.name = char(N(i).name);
    node_info.type = 'TN_HAPS';
    % HAPS have lat/lon
    if exist('haps_locations', 'var') && ~isempty(haps_locations)
        haps_idx = i - space_nodes - ground_nodes;
        if haps_idx <= size(haps_locations, 1)
            node_info.latitude = haps_locations(haps_idx, 1);
            node_info.longitude = haps_locations(haps_idx, 2);
            node_info.altitude = haps_altitude;
        end
    end
    nodes_struct.haps = [nodes_struct.haps; node_info];
end

fprintf('  Extracted: %d MEO, %d LEO, %d Ground, %d HAPS nodes\n', ...
    length(nodes_struct.meo), length(nodes_struct.leo), ...
    length(nodes_struct.ground), length(nodes_struct.haps));

end

function slot_data = extract_slot_data(slot_num)
% Extract data for a specific time slot

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
        if gs_idx > 0 && gs_idx <= numel(gs)
            pos.latitude = gs(gs_idx).Latitude;
            pos.longitude = gs(gs_idx).Longitude;
            pos.altitude = 0;
        end
    elseif strcmp(pos.type, 'TN_HAPS') && exist('haps_locations', 'var')
        % HAPS
        haps_idx = i - space_nodes - ground_nodes;
        if haps_idx > 0 && haps_idx <= size(haps_locations, 1)
            pos.latitude = haps_locations(haps_idx, 1);
            pos.longitude = haps_locations(haps_idx, 2);
            pos.altitude = haps_altitude;
        end
    end
    
    % Domain assignment
    if isfield(N_slot(i), 'domain')
        pos.domain = N_slot(i).domain;
    else
        pos.domain = 0;
    end
    
    % Controller assignment
    if isfield(N_slot(i), 'con')
        pos.controller = N_slot(i).con;
    else
        pos.controller = i; % Self-assignment
    end
    
    node_positions = [node_positions; pos];
end

slot_data.nodes = node_positions;

% Extract domain information
unique_domains = unique([node_positions.domain]);
domain_list = [];

for d = 1:length(unique_domains)
    domain_info = struct();
    domain_info.id = unique_domains(d);
    domain_info.members = [node_positions([node_positions.domain] == unique_domains(d)).id];
    domain_list = [domain_list; domain_info];
end

slot_data.domains = domain_list;

% Extract COMOSAT hierarchical controller info (if available)
if exist('x', 'var') && exist('y', 'var')
    slot_data.hierarchical = struct();
    slot_data.hierarchical.controllers = find(x == 1)'; % Master controllers
    slot_data.hierarchical.assignments = y; % Switch-to-controller assignments
end

% Extract links (if available)
if exist('adj', 'var') && exist('r', 'var') && exist('D', 'var')
    links = [];
    for i = 1:node
        for j = i+1:node
            if adj(i,j) == 1
                link_info = struct();
                link_info.source = i;
                link_info.target = j;
                link_info.data_rate = r(i,j);
                link_info.distance = D(i,j);
                links = [links; link_info];
            end
        end
    end
    slot_data.links = links;
    fprintf('    Extracted %d links\n', length(links));
end

fprintf('    Slot %d: %d nodes, %d domains\n', slot_num, node, length(unique_domains));

end

