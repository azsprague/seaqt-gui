function Phase2_Electron()

%% Generate Electron Eigenstates and Relaxation Time
clear all;
load tmp/System_description.mat;

% Get electron file path arrays from JSON data
electron_ev_paths = gui_json_data.electron_ev_paths;
electron_dos_paths = gui_json_data.electron_dos_paths;
electron_tau_paths = gui_json_data.electron_tau_paths;

% Get block ("subsystem") parameter arrays from JSON data
block_sizes = gui_json_data.block_sizes;
fermi_energies = gui_json_data.fermi_energies;
group_velocities = gui_json_data.electron_group_velocities;     % Not used?
relax_times = gui_json_data.electron_relaxation_times;
effective_masses = gui_json_data.electron_effective_masses;

% Prepare finished arrays
tau_e = [];
E_sys_e = [];
dNdE_sys_e = [];

% Loop over all electron files (total number of blocks or "subsystems")
for i = 1:(gui_json_data.number_of_blocks)

    % Get current electron files
    E_sys_name = string(electron_ev_paths(i));
    E_sys_dos_name = string(electron_dos_paths(i));
    E_sys_tau_name = string(electron_tau_paths(i));

    % Convert files to arrays
    E_sys = table2array(readtable(E_sys_name));
    E_sys_dos = table2array(readtable(E_sys_dos_name));

    % Check for existence of tau file
    if strcmp(E_sys_tau_name, "")
        has_tau_file = 0;
    else
        E_sys_tau = table2array(readtable(E_sys_tau_name));
        has_tau_file = 1;
    end

    % Get current block parameters
    fermi = fermi_energies(i) * 1.60218 * 10^(-19);     % Fermi level of electron DOS (not used?)
    ab = block_sizes(i);                                % Size of block ("subsystem")
    ef = effective_masses(i);                           % Electron effective mass
    bt = relax_times(i);                                % Electron relaxation time

    % Loop over all rows in current arrays
    for j = 1:(length(E_sys_dos))

        % Universal electron energy in Joules
        E_sys_e_single(j) = E_sys(j) * 1.60218e-19;     %% e-19?
        
        % Universal electron DOS in 1/Volume
        dNdE_sys_e_single(j) = E_sys_dos(j) / (1.97e-28);
        
        if has_tau_file
            % Pull tau value from array
            tau_e_single(j) = E_sys_tau(j);
        else
            % Calculate tau value
            tau_e_single(j) = abs((3 * m_e * ef * ab^2 / (2*bt)) / E_sys_e_single(j));
        end

    end

    % Append current electron values to finished arrays
    tau_e = [tau_e; tau_e_single.'];                   
    E_sys_e = [E_sys_e; E_sys_e_single.'];           
    dNdE_sys_e = [dNdE_sys_e; dNdE_sys_e_single.'];
end

save tmp/Electron.mat tau_e E_sys_e dNdE_sys_e E_sys_e_single
