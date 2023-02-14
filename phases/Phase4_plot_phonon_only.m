clear all;
load System_description.mat;

max_T_index = 12000;15300;      %time range to plot

%% electron
load Time_Evolution.mat;

T = T(1:100:max_T_index);                                   %time
y_T = y_T(1:100:max_T_index,1:System_length_e*System_num);  %solution of equation of motion for electron
E_sys = E_sys(1:System_length_e*System_num);                %band structure
dNdE_sys = dNdE_sys(1:System_length_e*System_num);          %density of states

S_y = -y_T+log(exp(y_T)+1)+y_T./(exp(y_T)+1);               %entropy entribution from a single band
S_T_e = sum(S_y.*(ones(length(T),1)*dNdE_sys'),2);          %total electron entropy

%% phonon
load Time_Evolution.mat;

T = T(1:100:max_T_index);
y_T = y_T(1:100:max_T_index,System_length_e*System_num+1:System_length*System_num); %solution of equation of motion for phonon 
E_sys = E_sys(System_length_e*System_num+1:System_length*System_num);               %phonon eigenenergy
dNdE_sys = dNdE_sys(System_length_e*System_num+1:System_length*System_num);         %phonon density of states

beta_T = y_T./(ones(length(T),1)*E_sys');               % 1/k_bT for each mode

S_y = y_T-log(exp(y_T)-1)+y_T./(exp(y_T)-1);            %entropy entribution from a single phonon modes
S_T_ph = sum(S_y.*(ones(length(T),1)*dNdE_sys'),2);     %total phonon entropy

%% plot phonon temperature evolution, PRB, Fig.2a
figure(11); hold on; grid;
xlim([0,30]);
ylim([300,500]);
for i=[11 15 20]
    temp_T1 = 1/kb./beta_T(:,(i-1)*System_length_ph+25);    %plot acoustic phonon
    temp_T6 = 1/kb./beta_T(:,(i)*System_length_ph);         %plot optic phonon
    plot(T, temp_T1,'k-','LineWidth',2.5); 
    plot(T, temp_T6,'k--','LineWidth',2.5);
end
for i=[1 5 10]
    temp_T1 = 1/kb./beta_T(:,(i-1)*System_length_ph+25);    %plot acoustic phonon
    temp_T6 = 1/kb./beta_T(:,(i)*System_length_ph);         %plot optic phonon
    plot(T, temp_T1,'r-','LineWidth',2.5);  
    plot(T, temp_T6,'r--','LineWidth',2.5);
end

set(gca, 'FontSize', 12);
xlabel('Dimensionless Time', 'fontsize', 14);
ylabel('Phonon Temperature (K)', 'fontsize', 14)
legend('Acoustic phonon','Optical phonon');
text(-5,500+(500-300)/20,'(a)','fontsize',16,'fontWeight','bold');


%% plot system entropy generation, PRB, Fig.2b
figure(12); hold on;
xlim([0,30]);
plot(T,S_T_ph*kb+S_T_e*kb,'LineWidth',2.5);
set(gca, 'FontSize', 12);
xlabel('Dimensionless Time', 'fontsize', 14);
ylabel('Total Entropy (J/K)', 'fontsize', 14);
text(-5,5.78+(5.78-5.6)/20,'(b)','fontsize',16,'fontWeight','bold');