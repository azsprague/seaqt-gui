function Phase4_plot()

clear all;
load System_description.mat;

%% prepare electron results
load Time_Evolution.mat; % load solution of equation of motion
max_T_index=floor(length(T)/100)*100;
T = T(1:100:max_T_index);       % Time
y_T = y_T(1:100:max_T_index,1:System_length_e*System_num); %solution of equation of motion
E_sys = E_sys(1:System_length_e*System_num);        %band structure
dNdE_sys = dNdE_sys(1:System_length_e*System_num);  %density of state
tau_sys=tau(1:System_length*System_num);

%% Time evolutions of electron properties
p_y = 1./(exp(y_T)+1);                          % occupation probability of every band (variable f for time/100 and systemlength_e*System_num)

N_y_T = p_y.*(ones(length(T),1)*dNdE_sys');     % contribution from each band to the system electron number
E_y_T = N_y_T.*(ones(length(T),1)*E_sys');      % contribution from each band to the system energy

N_T_e = sum(N_y_T,2);                              % total electron number
E_T_e = sum(E_y_T,2);                              % total energy
beta_T = y_T./(ones(length(T),1)*E_sys');  

%Save values for later
electron_ev=E_sys;
electron_dos=dNdE_sys;
electron_beta=beta_T;
electron_tau=tau_sys;
electron_y_T=y_T;
electron_p_y=p_y;
electron_N_y_T=N_y_T;
electron_length=length(E_sys)/System_num;
%% Plot electron results
% electron temperature
figure('Visible', 'off'); hold on; grid;
T_e = [];
for j = 1:max_T_index/100
    T_e_T = [];                 
    for i=[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20]
        temp_y = y_T(j,(i-1)*System_length_e+1:i*System_length_e);
        T_e_1 = [ones(System_length_e,1) E_sys(1:System_length_e)./kb]\temp_y';     % calculate temperature from y
        T_e_T = [T_e_T 1/T_e_1(2)];
    end
    T_e = [T_e; T_e_T];
end
plot(T,T_e(:,1),'k','LineWidth',2.5);
plot(T,T_e(:,5),'g','LineWidth',2.5);
plot(T,T_e(:,10),'b','LineWidth',2.5);
plot(T,T_e(:,11),'r','LineWidth',2.5);
plot(T,T_e(:,15),'c','LineWidth',2.5);
plot(T,T_e(:,20),'m','LineWidth',2.5);

set(gca, 'FontSize', 18);
xlabel('Time (seconds)', 'fontsize', 18);
ylabel('Electron Temperature (K)', 'fontsize', 18)
title('Electron Temperature vs. Time')
text(-5,500+(500-300)/20,'(b)','fontsize',16,'fontWeight','bold');

exportgraphics(gca, 'Figures/1.png', 'ContentType', 'image');

% plot electron number
figure('Visible', 'off'); hold on; grid;
N_e = [];
for j = 1:max_T_index/100
    N_e_T = [];
    for i=[1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20]
        temp_N_y = N_y_T(j,(i-1)*System_length_e+1:i*System_length_e);
        N_e_T = [N_e_T sum(temp_N_y)];
    end
    N_e = [N_e; N_e_T];
end
plot(T,N_e(:,1),'k','LineWidth',2.5)
plot(T,N_e(:,5),'g','LineWidth',2.5)
plot(T,N_e(:,10),'b','LineWidth',2.5)
plot(T,N_e(:,11),'r','LineWidth',2.5)
plot(T,N_e(:,15),'c','LineWidth',2.5)
plot(T,N_e(:,20),'m','LineWidth',2.5)

set(gca, 'FontSize', 12);
xlabel('Time (seconds)', 'fontsize', 14);
ylabel('Electron Number (particle)', 'fontsize', 14);
title('Electron number vs. Time')

exportgraphics(gca, 'Figures/2.png', 'ContentType', 'image');

% plot electron energy, PRB Figure 4(b)
figure('Visible', 'off'); hold on; grid;

E_e = [];
for j = 1:max_T_index/100
    E_e_T = []; 
    for i=[1 5 10 11 15 20]
        temp_E_y = E_y_T(j,(i-1)*System_length_e+1:i*System_length_e);
        E_e_T = [E_e_T sum(temp_E_y)];
    end
    E_e = [E_e; E_e_T];
end
plot(T,E_e(:,1),'k','LineWidth',2.5)
plot(T,E_e(:,2),'g','LineWidth',2.5)
plot(T,E_e(:,3),'b','LineWidth',2.5)
plot(T,E_e(:,4),'r','LineWidth',2.5)
plot(T,E_e(:,5),'c','LineWidth',2.5)
plot(T,E_e(:,6),'m','LineWidth',2.5)

set(gca, 'FontSize', 12);
xlabel('Time (seconds)', 'fontsize', 14);
ylabel('Electron Energy (J)', 'fontsize', 14)
title('Interface, electric field, 300 K. Electron Energy vs. Time') 
text(-5,93.2+(93.2-91.8)/20,'(b)','fontsize',16,'fontWeight','bold');

exportgraphics(gca, 'Figures/3.png', 'ContentType', 'image');

% plot electrical conductivity
figure('Visible', 'off'); hold on; grid;
e_charge=1.60217663e-19; %in columbs
ej=1.60218e-19; %ev to J
ab=1e-7; %size of subsystems
boltz=1.380649e-23;
em=9.109e-31;
E_c=[];
for j=1:max_T_index/100
    E_c_T=[];
    for i=[1 5 10 11 15 20]
        up=0;
        for k=1:System_length_e
            am=(i-1)*System_length_e+k;

            fi=(e_charge^2)/(boltz*T_e(j,i));
            se=(ab^2) / electron_tau(am);
 
            temp=electron_y_T(j,am);
            th=exp(temp)/((exp(temp)+1)^2);
            fr=electron_dos(am);
            ff=electron_ev((i-1)*System_length_e+2)-electron_ev((i-1)*System_length_e+1);
 
            up=up+fi*se*th*fr*ff; 
        end
        mb=up;
        comb=mb;
    E_c_T=[E_c_T comb];
    end
    E_c=[E_c; E_c_T];
end
plot(T,E_c(:,1),'k','LineWidth',2.5)
plot(T,E_c(:,2),'g','LineWidth',2.5)
plot(T,E_c(:,3),'b','LineWidth',2.5)
plot(T,E_c(:,4),'r','LineWidth',2.5)
plot(T,E_c(:,5),'c','LineWidth',2.5)
plot(T,E_c(:,6),'m','LineWidth',2.5)
set(gca,'FontSize', 12);
xlabel('Time (seconds)', 'fontsize', 14);
ylabel('Electrical Conductivity (Ohms^-1 cm^-1)','fontsize',14);
title('Electrical Conductivity vs. Time')

exportgraphics(gca, 'Figures/4.png', 'ContentType', 'image');

%% Seebeck Coefficient
figure('Visible', 'off'); hold on; grid;

echarge=1.60217663e-19;
T_n=[];
for j=1:max_T_index/100
    T_n_T=[];
    for i=[1 5 10 11 15 20]
        temp_t_s=0;
        up=0;
        down=0;
        for k=1:System_length_e
            len=(i-1)*System_length_e+k;
            ch=electron_ev((i-1)*System_length_e+2)-electron_ev((i-1)*System_length_e+1);
            temp=electron_y_T(j,len);
            beg=(e_charge^2*(-electron_dos(len))*ab^2 / (electron_tau(len)));
            fez=exp(temp)/(boltz*T_e(j,i)*(exp(temp)+1)^2);
            up=up+((electron_ev(len)+Ef_sys_e(len))*fez*beg*ch);
            down=down+beg*fez*ch;
        end
        temp_t_s=temp_t_s + (-1/(e_charge*T_e(j,i)))*up/down;
        T_n_T=[T_n_T temp_t_s];
    end
    T_n=[T_n; T_n_T];
end
        
plot(T,T_n(:,1),'k','LineWidth',2.5);
plot(T,T_n(:,2),'g','LineWidth',2.5);
plot(T,T_n(:,3),'b','LineWidth',2.5);
plot(T,T_n(:,4),'r','LineWidth',2.5);
plot(T,T_n(:,5),'c','LineWidth',2.5);
plot(T,T_n(:,6),'m','LineWidth',2.5);
xlabel('Time (seconds)','fontsize',14);
ylabel('Seebeck coefficient','fontsize',14);
title('Seebeck coefficient vs. Time','fontsize',14);

exportgraphics(gca, 'Figures/5.png', 'ContentType', 'image');

%% prepare phonon results
load Time_Evolution.mat;

T = T(1:100:max_T_index);
y_T = y_T(1:100:max_T_index,System_length_e*System_num+1:System_length*System_num);
E_sys = E_sys(System_length_e*System_num+1:System_length*System_num);
dNdE_sys = dNdE_sys(System_length_e*System_num+1:System_length*System_num);
tau_sys = tau(System_length_e*System_num+1:System_length*System_num);
p_y = 1./(exp(y_T)-1);                          % occupation probability of every mode

N_y_T = p_y.*(ones(length(T),1)*dNdE_sys');     % phonon number at each mode
E_y_T = N_y_T.*(ones(length(T),1)*E_sys');      % contribution from each mode to the system phonon energy
beta_T = y_T./(ones(length(T),1)*E_sys');       % 1/k_bT for each mode

E_T_ph = sum((N_y_T.*(ones(length(T),1)*E_sys')),2);    % total phonon energy

phonon_ev=E_sys;
phonon_dos=dNdE_sys;
phonon_beta=beta_T;
phonon_tau=tau_sys;
phonon_y_T=y_T;
phonon_p_y=p_y;
phonon_length=length(E_sys)/System_num;

%% plot phonon results
% plot phonon temperature, PRB Figure 3(a)
figure('Visible', 'off'); hold on; grid;
level_display = [];
for i=[11 15 20]
       temp_T1= 1/kb./beta_T(:,(i-1)*System_length_ph+25);
    if i == 11
        plot(T, temp_T1,'r','LineWidth',2.5);
    elseif i == 15
        plot(T,temp_T1,'c','LineWidth',2.5)
    elseif i == 20
        plot(T,temp_T1,'m','LineWidth',2.5)
    end
end
for i=[1 5 10]
    temp_T1 = 1/kb./beta_T(:,(i-1)*System_length_ph+25);        %plot acoustic phonon
    if i == 1
        plot(T, temp_T1,'k','LineWidth',2.5); 
    elseif i == 5
        plot(T,temp_T1,'g','LineWidth',2.5)
    elseif i==10
        plot(T,temp_T1,'b','LineWidth',2.5)
    end
end
set(gca, 'FontSize', 12);
xlabel('Time (seconds)', 'fontsize', 14);
ylabel('Phonon Temperature (K)', 'fontsize', 14)
title('Phonon Temperature vs. Time')
text(-5,500+(500-300)/20,'(a)','fontsize',16,'fontWeight','bold');

exportgraphics(gca, 'Figures/6.png', 'ContentType', 'image');

% plot phonon energy evolution, PRB Figure 4(c)
figure('Visible', 'off'); hold on; grid;
for i=[1 5 10]
    temp_E = E_y_T(:,(i-1)*System_length_ph+1:(i)*System_length_ph);
    if i==1
        plot(T,sum(temp_E,2),'k','LineWidth',2.5)
    elseif i==5
        plot(T,sum(temp_E,2),'g','LineWidth',2.5)
    elseif i==10
        plot(T,sum(temp_E,2),'b','LineWidth',2.5)
    end
end
for i=[11 15 20]
    temp_E = E_y_T(:,(i-1)*System_length_ph+1:(i)*System_length_ph);
    if i==11
        plot(T,sum(temp_E,2),'r','LineWidth',2.5)
    elseif i==15
        plot(T,sum(temp_E,2),'c','LineWidth',2.5)
    elseif i==20
        plot(T,sum(temp_E,2),'m','LineWidth',2.5)
    end
end
set(gca, 'FontSize', 12);
xlabel('Time (seconds)', 'fontsize', 14);
ylabel('Phonon Energy (J)', 'fontsize', 14)
title('Phonon Energy vs. Time')
text(-5,90+(90-30)/20,'(c)','fontsize',16,'fontWeight','bold');

exportgraphics(gca, 'Figures/7.png', 'ContentType', 'image');

%% thermal conductivity
figure('Visible', 'off'); hold on; grid;

hp=1.054571817e-34; %h bar planks
eh=1.509190311e33; % Joules to hertz
boltz=1.380649e-23;
ej=1.60218e-19; %ev to joules
%% electron/phonon values

T_c=[];
for j=1:max_T_index/100
    T_c_T = [];
    T_e_T = [];
    T_p_T = [];
    for i=[1 5 10 11 15 20]
        temp_t_c=0;
        temp_e_c=0;
        for k=1:phonon_length-1
            temp_ph = 1/kb./phonon_beta(j,(i-1)*System_length_ph+25);
            at=(i-1)*phonon_length+k;
            temp=phonon_y_T(j,at);
            cw=hp * phonon_ev(at)^2 * (phonon_dos(at)) * exp(temp) / (boltz*temp_ph^2 * (exp(temp)+1)^2);
            ch=eh*(phonon_ev(at+1)-phonon_ev(at));
            temp_t_c=temp_t_c + (ab^2 * cw * ch / (phonon_tau(at)));
        end
        for k=1:electron_length-1
            temp_e = T_e(j,i);
            at=(i-1)*electron_length+k;
            temp=electron_y_T(j,at);
            cw=hp *electron_ev(at) * (electron_dos(at))  * (electron_ev(at)+Ef_sys_e(at))* exp(temp) / (boltz*temp_e^2 * (exp(temp)-1)^2);
            ch=eh * (electron_ev(at+1)-electron_ev(at));
            temp_e_c=temp_e_c + (ab^2 * cw * ch/ (electron_tau(at)));
        end
        temp_t_c=temp_t_c/300;
        temp_e_c=temp_e_c/300;
        temp_eq=temp_t_c + temp_e_c;
        T_c_T=[T_c_T temp_eq];
        T_e_T=[T_e_T temp_e_c];
        T_p_T=[T_p_T temp_t_c];
    end
    T_c=[T_c; T_c_T];
end 

plot(T,T_c(:,1),'k','LineWidth',2.5);
plot(T,T_c(:,2),'g','LineWidth',2.5);
plot(T,T_c(:,3),'b','LineWidth',2.5);
plot(T,T_c(:,4),'r','LineWidth',2.5);
plot(T,T_c(:,5),'c','LineWidth',2.5);
plot(T,T_c(:,6),'m','LineWidth',2.5);
set(gca,'FontSize',12);
xlabel('Time (seconds)','fontsize',14);
ylabel('Thermal Conductivity','fontsize',14);
title('Thermal Conductivity vs. Time','fontsize',14);

exportgraphics(gca, 'Figures/8.png', 'ContentType', 'image');

figure('Visible', 'off'); hold on; grid;

zt=[];
for i=1:max_T_index/100
    zt_T=[];
    for i=[1 2 3 4 5 6]
        zt_temp= E_c(j,i) * T_n(j,i)^2 * (T_e(j,i)) / T_c(j,i);
        zt_T=[zt_T zt_temp];
    end
    zt = [zt; zt_T];
end

plot(T,zt(:,1),'k','Linewidth',2.5);
plot(T,zt(:,2),'g','Linewidth',2.5);
plot(T,zt(:,3),'b','Linewidth',2.5);
plot(T,zt(:,4),'r','Linewidth',2.5);
plot(T,zt(:,5),'c','Linewidth',2.5);
plot(T,zt(:,6),'m','Linewidth',2.5)
xlabel("Time (seconds)",'fontsize',14);
ylabel("ZT factor","fontsize",14)
title("ZT Factor vs. time",'fontsize',14)

exportgraphics(gca, 'Figures/9.png', 'ContentType', 'image');
