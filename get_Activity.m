%Equation of motion for transport, Eq.20 PRB for two neighbor local systems
function dydt = get_Activity(y, particle_type, E_sys, dNdE_sys, tau) 

if particle_type==0     %electron
    [beta_0, gamma_0] = get_bg_e (y, E_sys, dNdE_sys, tau);
    y_0=E_sys.*beta_0+gamma_0;
else                    %phonon
    [beta_0] = get_bg_ph (y, E_sys, dNdE_sys, tau);
    y_0=E_sys.*beta_0;
end

dydt = -(y-y_0)./tau;

end