%% Equation of motion of electron-phonon coupling Sec.V.C
function [dydt_e, dydt_ph] = get_Activity_e_ph(y_e, E_sys_e, dNdE_sys_e, tau_e, y_ph, E_sys_ph, dNdE_sys_ph, tau_ph) %for e-ph interaction

N_y_e     = 1./(1+exp(y_e));
A_nn_y_e  = N_y_e.*(1-N_y_e);

A_nn_e = sum(A_nn_y_e.*dNdE_sys_e./tau_e);

A_ne_y_e = E_sys_e.*A_nn_y_e;
A_ne_e = sum(A_ne_y_e.*dNdE_sys_e./tau_e);
clear A_ne_y_e;
A_ee_y_e = E_sys_e.^2.*A_nn_y_e;
A_ee_e = sum(A_ee_y_e.*dNdE_sys_e./tau_e);
clear A_ee_y_e;
A_ns_y_e = y_e.*A_nn_y_e;
A_ns_e = sum(A_ns_y_e.*dNdE_sys_e./tau_e);
clear A_ns_y_e;
A_es_y_e = y_e.*E_sys_e.*A_nn_y_e;
A_es_e = sum(A_es_y_e.*dNdE_sys_e./tau_e);
clear A_es_y_e;

N_y_ph    = 1./(exp(y_ph)-1);
A_nn_y_ph  = N_y_ph.*(1+N_y_ph);   

A_ee_y_ph = E_sys_ph.^2.*A_nn_y_ph;
A_ee_ph = sum(A_ee_y_ph.*dNdE_sys_ph./tau_ph);
clear A_ee_y_ph;

A_es_y_ph = y_ph.*E_sys_ph.*A_nn_y_ph;
A_es_ph = sum(A_es_y_ph.*dNdE_sys_ph./tau_ph);
clear A_es_y_ph;

C1=(A_ee_e+A_ee_ph)*A_nn_e-A_ne_e*A_ne_e;
C2=(A_es_e+A_es_ph)*A_nn_e-A_ne_e*A_ns_e;
C3=(A_es_e+A_es_ph)*A_ne_e-(A_ee_e+A_ee_ph)*A_ns_e;

beta_0 = C2/C1;
gamma_0 = -C3/C1;

y_0_e  = E_sys_e.*beta_0+gamma_0;
dydt_e = -(y_e-y_0_e)./tau_e;

y_0_ph = E_sys_ph.*beta_0;
dydt_ph= -(y_ph-y_0_ph)./tau_ph;
end