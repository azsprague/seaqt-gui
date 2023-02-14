clear all;
load System_description.mat;
load Phonon.mat;
load Electron.mat;

global System_num;
System_num = 20;                %local system number
global System_length;
global System_length_e;
global System_length_ph;

%% Phonon initial condition
System_length_ph = length(E_sys_ph_single);

T_a_ph=500;         % initial temperature for phonon local system 1 to 10
T_b_ph=300;         % initial temperature for phonon local system 11 to 20
T_sys_ph = ones(System_num*System_length_ph,1)*T_b_ph;
T_sys_ph(1:System_length_ph*System_num/2) = T_a_ph;

tau_ph =[];
E_sys_ph = [];
dNdE_sys_ph =[];
for i=1:System_num
tau_ph = [tau_ph; tau_ph_single];                       %phonon relaxation time
E_sys_ph = [E_sys_ph; E_sys_ph_single];                 %assemble 20 phonon local system eigen-struccture
dNdE_sys_ph = [dNdE_sys_ph; dNdE_sys_ph_single];
end
Activity_sys_ph =1/kb./T_sys_ph.*E_sys_ph;      %calculate system intial y, see Eq, 19 in PRB 97, 024308 (2018)

%% Electron initial condition
System_length_e = length(E_sys_e_single);

T_a_e=500;      % initial temperature for electron local system 1 to 10
T_b_e=300;      % initial temperature for electron local system 11 to 20
T_sys_e = ones(System_num*System_length_e,1)*T_b_e;                 %define electron temperature of local system 11 to 20
T_sys_e(1:System_length_e*System_num/2) = T_a_e;                    %define electron temperature of local system 1 to 10
Initial_beta_e = 1./T_sys_e./kb;                                    %beta=1/kb/T

Fermi_level_a = -(min(E_sys_e_single)+max(E_sys_e_single))/3;       %define fermi level of local system 1 to 10
Fermi_level_b = -(min(E_sys_e_single)+max(E_sys_e_single))/3;       %define fermi level of local system 11 to 20
Ef_sys_e = ones(System_num*System_length_e,1)*Fermi_level_a;
Ef_sys_e(1:System_length_e*System_num/2) = Fermi_level_b;           
Initial_gamma =Ef_sys_e.*Initial_beta_e;

tau_e =[];
E_sys_e = [];
dNdE_sys_e =[];
for i=1:System_num
tau_e = [tau_e; tau_e_single];                   %electron relaxation time
E_sys_e = [E_sys_e; E_sys_e_single];             %combine 20 electron local system eigen-struccture
dNdE_sys_e = [dNdE_sys_e; dNdE_sys_e_single];
end

Activity_sys_e = Initial_beta_e.*E_sys_e+Initial_gamma; %calculate system initial y, see Eq, 19 in PRB 97, 024308 (2018)


System_length = System_length_e+System_length_ph;       %assemble electron and phonon system together

global E_sys;
global dNdE_sys;
global tau;
E_sys = [E_sys_e; E_sys_ph];
dNdE_sys = [dNdE_sys_e; dNdE_sys_ph];
tau = [tau_e; tau_ph];
Activity_sys = [Activity_sys_e; Activity_sys_ph];       %assemble electron y and phonon y

%% Run equation of motion of y
tic;
ts = 0;
tf = 20*max(tau);                                                         % finishing time
options   = odeset('AbsTol',1e-40,'RelTol',1e-5);
[T,y_T] = ode45(@CSEA_Sys_single_y_ph_only,[ts tf],Activity_sys,options); % run equation of motion of y, PRB Eq.20
save Time_Evolution.mat;                                                  % y_T T tau dNdE_sys E_sys System_length_ph System_num;
toc;