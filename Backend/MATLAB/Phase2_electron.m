function Phase2_electron()

%% Generate Electron Eigenstates and Relaxation Time
clear all;
load System_description.mat;

% Read in seperate electron DOS spreadsheets
E_sys = table2array(readtable(gui_json_data.e_ev_path));
E_sys_dos = table2array(readtable(gui_json_data.e_dos_path));

h=6.62607015e-34; % Planck's Constant
fermi=6 * 1.60218 * 10^(-19); %This is the Fermi level of electron DOS
for i = 1:(length(E_sys_dos))
        %Universal electron energy in Joules
        E_sys_e_single(i)=E_sys(i)*1.60218e-19;
        
        %Universal electron DOS in 1/Volume
        dNdE_sys_e_single(i)=E_sys_dos(i)/(1.97e-28);
        
        %Calculate relaxation time
        mr=(dNdE_sys_e_single(i)*h^3/(sqrt(2*abs((E_sys_e_single(i)-fermi))^3)*8*pi))^(2/3);
        %Relaxation time calc. in PBR eq.41
        % tau_e_single(i)=abs(1*mr/E_sys_e_single(i));
        
        %Can't have 0 relaxation time
        % if tau_e_single(i)==0
            tau_e_single(i)=abs(1*(9.1e-31)/E_sys_e_single(i));
        % end
end
%Need systems in this format
E_sys_e_single = E_sys_e_single.';
dNdE_sys_e_single = dNdE_sys_e_single.';
tau_e_single=tau_e_single.';

save Electron.mat E_sys_e_single dNdE_sys_e_single tau_e_single;