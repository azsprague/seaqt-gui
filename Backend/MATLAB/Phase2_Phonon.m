function Phase2_Phonon()

%% Generate Phonon Eigenstates and Relaxation Time
clear all;
load tmp/System_description.mat;

% Get phonon file path arrays from JSON data
phonon_ev_paths = gui_json_data.phonon_ev_paths;
phonon_dos_paths = gui_json_data.phonon_dos_paths;
phonon_tau_paths = gui_json_data.phonon_tau_paths;

% Get block parameter arrays from JSON data
block_sizes = gui_json_data.block_sizes;
group_velocities = gui_json_data.phonon_group_velocities;
relax_times = gui_json_data.phonon_relaxation_times;

% Prepare finished arrays
tau_ph = [];
e_sys_ph = [];
dNdE_sys_ph = [];

% Loop over all phonon files (total number of blocks or "subsystems")
for i = 1:(gui_json_data.number_of_blocks)

    % Get current phonon files
    e_sys_name = string(phonon_ev_paths(i));
    e_sys_dos_name = string(phonon_dos_paths(i));
    e_sys_tau_name = string(phonon_tau_paths(i));

    % Convert files to arrays
    e_sys = table2array(readtable(e_sys_name));
    e_sys_dos = table2array(readtable(e_sys_dos_name));

    % Check for existence of tau file
    if strcmp(e_sys_tau_name, "")
        has_tau_file = 0;
    else
        e_sys_tau = table2array(readtable(e_sys_tau_name));
        has_tau_file = 1;
    end

    % Get current block parameters
    ab = block_sizes(i);            % Size of block ("subsystem")
    vel = group_velocities(i);      % Phonon group velocity
    tau = relax_times(i);           % Phonon relaxation time
    
    % Loop over all rows in current arrays
    for j = 1:(length(e_sys_dos))
        
        % Universal phonon energy in Joules
        e_sys_ph_single(j) = e_sys(j) * (1.60218e-22);  %% e-22?
        
        % Universal phonon DOS in 1/Volume
        dNdE_sys_ph_single(j) = e_sys_dos(j) / (1.97e-28);
        
        if has_tau_file
            % Pull tau value from array
            tau_ph_single(j) = e_sys_tau(j);
        else
            % Calculate tau value (in PBR eq. 49)
            tau_ph_single(j) = (ab / vel)^2 / tau;
        end

    end

    % Append current phonon values to finished arrays
    tau_ph = [tau_ph; tau_ph_single.'];                   
    e_sys_ph = [e_sys_ph; e_sys_ph_single.'];           
    dNdE_sys_ph = [dNdE_sys_ph; dNdE_sys_ph_single.'];

end

save tmp/Phonon.mat tau_ph e_sys_ph dNdE_sys_ph
