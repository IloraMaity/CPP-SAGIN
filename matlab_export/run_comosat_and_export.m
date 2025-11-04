% =========================================================================
% run_comosat_and_export.m
% =========================================================================
% Simple wrapper to run COMOSAT and export to Mininet format
% Run this from the MATLAB command window in the project root directory
% =========================================================================

function run_comosat_and_export(num_slots)
% RUN_COMOSAT_AND_EXPORT Run COMOSAT simulation and export to Mininet
% 
% Usage from MATLAB command window:
%   run_comosat_and_export(10)    % Export 10 time slots
%   run_comosat_and_export(97)    % Export 97 time slots
%
% Inputs:
%   num_slots: number of time slots to export (default: 10)

if nargin < 1
    num_slots = 10;
end

fprintf('\n===============================================\n');
fprintf('COMOSAT Simulation and Mininet Export\n');
fprintf('===============================================\n');
fprintf('Exporting %d time slots\n', num_slots);

% Step 1: Load scenario data
fprintf('\n[1/3] Loading scenario data...\n');
if(exist('scenario_sagin_cpp.mat', 'file'))
    load('scenario_sagin_cpp.mat');
    fprintf('  ✓ Loaded scenario_sagin_cpp.mat\n');
else
    fprintf('  ✗ scenario_sagin_cpp.mat not found\n');
    error('Please ensure scenario_sagin_cpp.mat exists in the current directory');
end

fprintf('  Running SetSimulationParams...\n');
SetSimulationParams;

% Override slotCount to match requested number of slots
slotCount = num_slots;
fprintf('  ✓ Simulation parameters set (slotCount = %d)\n', slotCount);

% Step 2: Run CPPsatEnhanced
fprintf('\n[2/3] Running CPPsatEnhanced algorithm...\n');
fprintf('  This may take several minutes...\n');
tic;
CPPsatEnhanced;
elapsed_time = toc;
fprintf('  ✓ CPPsatEnhanced completed in %.1f seconds\n', elapsed_time);

% Verify results
if ~exist('N_history', 'var')
    error('CPPsatEnhanced failed: N_history not created');
end
fprintf('  ✓ N_history has %d time slots\n', length(N_history));

if exist('x', 'var') && exist('y', 'var')
    fprintf('  ✓ x and y matrices created\n');
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

% Step 3: Export to Mininet format
fprintf('\n[3/3] Exporting to Mininet format...\n');
addpath('mininet_ryu_comosat/matlab_export');
export_to_mininet('COMOSAT', num_slots, 'mininet_ryu_comosat/topology/');

fprintf('\n===============================================\n');
fprintf('✓ Export Complete!\n');
fprintf('===============================================\n');
fprintf('Output file: mininet_ryu_comosat/topology/mininet_topology_data.json\n');
fprintf('You can now run Mininet simulation.\n');
fprintf('===============================================\n\n');

end

