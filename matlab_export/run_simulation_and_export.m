% =========================================================================
% run_simulation_and_export.m
% =========================================================================
% Wrapper script to run simulation and export data
% This should be run after executing the main simulation
% =========================================================================

function run_simulation_and_export(algorithm_type, num_slots)
% RUN_SIMULATION_AND_EXPORT Run simulation and export to Mininet format
% 
% Usage:
%   1. First run your simulation (e.g., KMPP or executeEnhanced)
%   2. Then call this function: run_simulation_and_export('KMPP', 10)
%
% Inputs:
%   algorithm_type: 'KMPP', 'COMOSAT', 'MCD', or 'HDS'
%   num_slots: number of time slots to export

if nargin < 1
    algorithm_type = 'KMPP';
end
if nargin < 2
    num_slots = 10;
end

fprintf('\n=== Running Simulation and Export ===\n');
fprintf('Algorithm: %s, Time Slots: %d\n', algorithm_type, num_slots);

% Check if we need to load scenario data
if ~exist('node', 'var')
    fprintf('\n--- Loading Scenario Data ---\n');
    
    % Load scenario data first (required for all algorithms)
    if(exist('scenario_sagin_cpp.mat', 'file'))
        load('scenario_sagin_cpp.mat');
        fprintf('Loaded scenario_sagin_cpp.mat\n');
        SetSimulationParams;
        % Override slotCount to match requested number of slots
        slotCount = num_slots;
        fprintf('Set simulation parameters (slotCount = %d)\n', slotCount);
    else
        fprintf('Warning: scenario_sagin_cpp.mat not found. Trying DefineConstellationwithHAPS...\n');
        DefineConstellationwithHAPS;
        SetSimulationParams;
        % Override slotCount to match requested number of slots
        slotCount = num_slots;
        fprintf('Set simulation parameters (slotCount = %d)\n', slotCount);
    end
end

% Check if we need to run simulation
if ~exist('N_history', 'var')
    fprintf('\n--- Running Simulation ---\n');
    
    % Run the appropriate simulation
    if strcmpi(algorithm_type, 'KMPP')
        KMPP;
    elseif strcmpi(algorithm_type, 'COMOSAT')
        % For COMOSAT, use CPPsatEnhanced (not CPPsat)
        CPPsatEnhanced;
    elseif strcmpi(algorithm_type, 'MCD')
        MCD;
    elseif strcmpi(algorithm_type, 'HDS')
        HDS;
    else
        error('Unknown algorithm type: %s', algorithm_type);
    end
end

% Note: For COMOSAT, x and y will be available in workspace after CPPsatEnhanced runs

% Verify N_history exists
if ~exist('N_history', 'var')
    error('N_history not created. Simulation may have failed.');
end

% Debug: Check all required variables exist
fprintf('\n--- Verifying Required Variables ---\n');
required_vars = {'node', 'meo_nodes', 'leo_nodes', 'ground_nodes', 'haps_count', ...
                 'space_nodes', 'slotDur', 'start_time', 'position', 'N_history'};
for i = 1:length(required_vars)
    if ~exist(required_vars{i}, 'var')
        fprintf('  ✗ Missing: %s\n', required_vars{i});
    else
        fprintf('  ✓ Found: %s\n', required_vars{i});
    end
end

fprintf('\n--- Exporting to Mininet Format ---\n');
export_to_mininet(algorithm_type, num_slots, 'mininet_ryu_comosat/topology/');

end

