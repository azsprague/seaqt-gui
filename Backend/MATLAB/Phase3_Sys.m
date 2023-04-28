function Phase3_Sys()

clear all;
load tmp/System_description.mat;
load tmp/Phonon.mat;
load tmp/Electron.mat;

global System_num;
global System_length;
global System_length_e;
global System_length_ph;

System_num = gui_json_data.number_of_blocks;
System_length = 0;
System_length_e = 0;
System_length_ph = 0;

block_temps = gui_json_data.block_temperatures;
run_type = gui_json_data.run_type;

% Electron (or both)
if run_type == 1 || run_type == 3

    % Electron initial parameters
    System_length_e = length(E_sys_e_single);
    T_sys_e = [];
    for i = 1:System_num
        T_sys_e = [T_sys_e; ones(System_length_e, 1) * block_temps(i)];
    end

    Ef_sys_e = [];
    Initial_beta_e = 1./T_sys_e./kb;                    
    
    % Get change in Fermi level with temperature
    Fermi_energies = gui_json_data.fermi_energies;
    Fermi_level = [];
    for i = 1:System_num
        Fermi_level = [Fermi_level, Fermi_energies(i) * 1.60218 * 10^(-19)];
    end
    
    for i = 1:System_num
    
        for k = 1:length(E_sys_e_single) 
            Ef_sys_e_temp = Fermi_level(i);
        end
    
        Ef_sys_e = [Ef_sys_e; ones(System_length_e, 1) * Ef_sys_e_temp];
    end

    Initial_gamma = Ef_sys_e.*Initial_beta_e;
    Activity_sys_e = Initial_beta_e.*E_sys_e+Initial_gamma;     % calculate system initial y, see Eq, 19 in PRB 97, 024308 (2018)

end

% Phonon (or both)
if run_type == 2 || run_type == 3

    % Phonon initial parameters
    System_length_ph = length(E_sys_ph_single);
    T_sys_ph = [];
    for i = 1:System_num
        T_sys_ph = [T_sys_ph; ones(System_length_ph, 1) * block_temps(i)];
    end
    
    Activity_sys_ph = 1/kb./T_sys_ph.*E_sys_ph;      % calculate system intial y, see Eq, 19 in PRB 97, 024308 (2018)

end

%% Combined parameters
System_length = System_length_e + System_length_ph;         % assemble electron and phonon system together

global E_sys;
global dNdE_sys;
global tau;

% If only running electron or phonon, create empty arrays
if run_type == 1
    E_sys_ph = [];
    dNdE_sys_ph = [];
    tau_ph = [];
    Activity_sys_ph = [];

elseif run_type == 2
    E_sys_e = [];
    dNdE_sys_e = [];
    tau_e = [];
    Activity_sys_e = [];

end

E_sys = [E_sys_e; E_sys_ph];
dNdE_sys = [dNdE_sys_e; dNdE_sys_ph];
tau = [tau_e; tau_ph];
Activity_sys = [Activity_sys_e; Activity_sys_ph];       % assemble electron y and phonon y

%% Run equation of motion of y
tic;
ts = 0;

% Extract time type and duration from gui
time_duration = gui_json_data.time_duration;
time_type = gui_json_data.time_type;
if time_type == 1
    tf = time_duration * min(tau);
elseif time_type == 2
    tf = time_duration * max(tau);
end

[ts tf];
options   = odeset('AbsTol',1e-7,'RelTol',1e-5);
[T,y_T] = ode45(@CSEA_Sys_single_y_ph_e,[ts tf],Activity_sys,options);  % run equation of motion of y, PRB Eq.20
save ('tmp/Time_Evolution.mat', '-v7.3');                               % y_T T tau dNdE_sys E_sys System_length_ph System_num;