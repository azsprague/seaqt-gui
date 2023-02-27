function Phase2_Phonon()

%% Generate Phonon Eigenstates and Relaxation Time
clear all;
load System_description.mat;

%Read in seperate Phonon DOS spreadsheets
E_sys = table2array(readtable(gui_json_data.p_ev_path));
E_sys_dos = table2array(readtable(gui_json_data.p_dos_path));

for i=1:length(E_sys_dos)
    %Universal phonon energy in Joules
    E_sys_ph_single(i)=E_sys(i)*(1.60218e-22);
    
    %Universal phonon DOS in 1/Volume
    dNdE_sys_ph_single(i)=E_sys_dos(i)/(1.97e-28);
    
    %Value for phonon relaxation in PBR eq. 49
    tau_ph_single(i)=1e-12;
end
%Need to be in this format
dNdE_sys_ph_single=dNdE_sys_ph_single.';
E_sys_ph_single=E_sys_ph_single.';
tau_ph_single=tau_ph_single.';
save Phonon.mat E_sys_ph_single dNdE_sys_ph_single tau_ph_single;