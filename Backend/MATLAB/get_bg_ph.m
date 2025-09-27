%% Calculate \beta_E and \beta_N in Eq.20 PRB for phonon, See appendix A
function beta_0 = get_bg_ph (y, E_sys, dNdE_sys, tau)
    N_y     = 1./(exp(y)-1);
    A_nn_y  = N_y.*(1+N_y);  

    A_ee_y = E_sys.^2.*A_nn_y;
    A_ee = sum(A_ee_y.*dNdE_sys./tau);
    clear A_ee_y;

    A_es_y = y.*E_sys.*A_nn_y;
    A_es = sum(A_es_y.*dNdE_sys./tau);
    clear A_es_y;

    C1 = A_ee;
    C2 = A_es;

    beta_0 = C2/C1;
end