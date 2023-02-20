%% Equation of motion without electron phonon coupling
function dmudt = CSEA_Sys_single_y_ph_only(t,y)
global tau;
global System_num;
global System_length_e
global System_length_ph
global System_length
global E_sys;
global dNdE_sys;

dmudt = zeros(System_num*System_length,1);
%"get_Activity" gives the y evolution resulted from the transport from one
%neighboring local system
%"get_Activity_e_ph" gives the y evolution resulted from electron-phonon
%coupling
for i = 1:System_num-1
    %% e-transport
    temp_e_index = System_length_e*(i-1)+1:System_length_e*(i+1);
    dmudt(temp_e_index)= dmudt(temp_e_index)+get_Activity(y(temp_e_index), 0, E_sys(temp_e_index), dNdE_sys(temp_e_index), tau(temp_e_index));
    %% ph-transport
    temp_ph_index = (System_length_ph*(i-1)+1:System_length_ph*(i+1))+System_length_e*System_num;
    dmudt(temp_ph_index)= dmudt(temp_ph_index)+get_Activity(y(temp_ph_index), 1, E_sys(temp_ph_index), dNdE_sys(temp_ph_index), tau(temp_ph_index));
end

%%%remove electron phonon coupling
% for i = 1:System_num
%     %% e-ph
%     temp_e_index = System_length_e*(i-1)+1:System_length_e*(i);
%     temp_ph_index = (System_length_ph*(i-1)+1:System_length_ph*(i))+System_length_e*System_num;
%     [get_Activity_e, get_Activity_ph]=get_Activity_e_ph(y(temp_e_index), E_sys(temp_e_index), dNdE_sys(temp_e_index), tau(temp_e_index), y(temp_ph_index), E_sys(temp_ph_index), dNdE_sys(temp_ph_index), tau(temp_ph_index));
%     
%     dmudt(temp_e_index)= dmudt(temp_e_index)+get_Activity_e;
%     dmudt(temp_ph_index)= dmudt(temp_ph_index)+get_Activity_ph;
% end

dmudt = real(dmudt);
end