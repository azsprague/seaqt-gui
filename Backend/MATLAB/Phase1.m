function Phase1()

clear all;

%% Constants
Na = 6.02214129e23;     % Avogadro number particles/mole
h  = 6.626068e-34;      % Plank constant J.s 
hr = 1.054571726e-34;   % J.s 
kb = 1.3806503e-23;     % Boltzmann constant J/K
kcal_eV = 2.611448e22;  % 1kcal / 1eV
pp = pi;                % pi
cc = 299792458;         % speed of light m/s
m_H = 3.34745e-27 / 2;  % mass of Hydrogen atom
m_e = 9.10938356e-31;   % electron mass

% Unit selection
sys = 'eV'; % 'J'
if strcmp(sys,'eV') == 1
    J_to_eV = 6.241509e18;   % 5.24151e18;
else
    J_to_eV = 1;
end

% Dimensions of a local system
lx = 1e-2; 
ly = 1e-2; 
lz = 1e-2; 
Vol = lx * ly * lz;     % units of m^3 

% Import data from GUI
gui_json_data = jsondecode(fileread('tmp/seaqt_prefs.json'));

save tmp/System_description.mat;
