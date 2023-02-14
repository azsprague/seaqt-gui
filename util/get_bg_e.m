%% Calculate \beta_E and \beta_N in Eq.20 PRB for electron, See appendix A
function [beta_0, gamma_0] = get_bg_e (y, E_sys, dNdE_sys, tau) 
    N_y     = 1./(1+exp(y));
    A_nn_y  = N_y.*(1-N_y);
   
    A_nn = sum(A_nn_y.*dNdE_sys./tau);

    A_ne_y = E_sys.*A_nn_y;
    A_ne = sum(A_ne_y.*dNdE_sys./tau);
    clear A_ne_y;
    A_ee_y = E_sys.^2.*A_nn_y;
    A_ee = sum(A_ee_y.*dNdE_sys./tau);
    clear A_ee_y;
    A_ns_y = y.*A_nn_y;
    A_ns = sum(A_ns_y.*dNdE_sys./tau);
    clear A_ns_y;
    A_es_y = y.*E_sys.*A_nn_y;
    A_es = sum(A_es_y.*dNdE_sys./tau);
    clear A_es_y;

    C1=A_ee*A_nn-A_ne*A_ne;
    C2=A_es*A_nn-A_ne*A_ns;
    C3=A_es*A_ne-A_ee*A_ns;

    beta_0 = C2/C1;
    gamma_0 = -C3/C1;
end