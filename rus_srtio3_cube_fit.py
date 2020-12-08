import mph
import numpy as np
import time
client = mph.Client()
from lmfit import minimize, Parameters, report_fit
##<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

filename = 'rus_srtio3_cube.mph'
model = client.load(filename)

nb_freq_in_comsol  = 20
nb_freq_to_compare = 12 # this one needs to be smaller

## Initial parameters >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
c11_ini = 321.49167  # in GPa
c11_int = [300, 350]  # in GPa
c11_vary = True

c23_ini = 103.52989  # in GPa
c23_int = [70, 130]  # in GPa
c23_vary = True

c44_ini = 124.91915   # in GPa
c44_int = [100, 150]  # in GPa
c44_vary = True

# nb_calls = 0

## Load the resonance data in MHz >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
freqs_data = 1e-6 * np.loadtxt("data/SrTiO3_RT_frequencies.dat", dtype="float", comments="#")

## Only select the first number of "freq to compare"
freqs_data = freqs_data[:nb_freq_to_compare]

## Initialize fit parameters >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
pars = Parameters()
pars.add("c11", value=c11_ini, vary=c11_vary, min=c11_int[0], max=c11_int[-1])
pars.add("c23", value=c23_ini, vary=c23_vary, min=c23_int[0], max=c23_int[-1])
pars.add("c44", value=c44_ini, vary=c44_vary, min=c44_int[0], max=c44_int[-1])

## Modifying COMSOL parameters >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
model.parameter('nb_freq', str(nb_freq_in_comsol))

## Residual function >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
def residual_func(pars):
    """Compute diff = freqs_sim - freqs_data"""

    start_total_time = time.time()

    ## Get fit parameters
    c11 = pars["c11"].value
    c23 = pars["c23"].value
    c44 = pars["c44"].value

    print("c11 = ", np.round(c11, 3), " GPa")
    print("c23 = ", np.round(c23, 3), " GPa")
    print("c44 = ", np.round(c44, 3), " GPa")

    ## Update elastic constants --------------------------------------------------
    model.parameter('c11', str(c11)+"[GPa]")
    model.parameter('c23', str(c23)+"[GPa]")
    model.parameter('c44', str(c44)+"[GPa]")

    ## Compute resonances --------------------------------------------------------
    model.solve('resonances')
    freqs_sim = model.evaluate('abs(freq)', 'MHz')
    model.clear()
    model.reset()

    print("---- Done in %.6s seconds ----" % (time.time() - start_total_time))

    ## Remove bad frequencies at the beginning
    index_ok = freqs_sim > 1e-4
    freqs_sim = freqs_sim[index_ok]

    ## Only select the first number of "freq to compare"
    freqs_sim = freqs_sim[:nb_freq_to_compare]

    return freqs_sim - freqs_data



## Run fit algorithm >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
out = minimize(residual_func, pars, method='differential_evolution')
# out = minimize(residual_func, pars, method='shgo',
#                sampling_method='sobol', options={"f_tol": 1e-16}, n = 100, iters=20)

## Display fit report >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
report_fit(out)

## Close COMSOL file without saving solutions in the file
client.clear()