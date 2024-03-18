from IHSetJaramillo21a import cal_Jaramillo21a, jaramillo21a
from IHSetCalibration import setup_spotpy
import xarray as xr
import os
import matplotlib.pyplot as plt
import spotpy as spt

# Avaliable methods: NSGAII, mle, mc, dds, mcmc, sa, abc, lhs, rope, sceua, demcz, padds, fscabc

# config = xr.Dataset(coords={'dt': 3,                # [hours]
#                             'switch_alpha_ini': 0,  # Calibrate the initial position? (0: No, 1: Yes)
#                             'Ysi': 2000,            # Initial year for calibration
#                             'Msi': 1,               # Initial month for calibration
#                             'Dsi': 1,               # Initial day for calibration
#                             'Ysf': 2005,            # Final year for calibration
#                             'Msf': 1,               # Final month for calibration
#                             'Dsf': 1,               # Final day for calibration
#                             'cal_alg': 'NSGAII',    # Avaliable methods: NSGAII
#                             'metrics': 'mss_nsse',  # Metrics to be minimized (mss_rmse, mss_rho, mss_rmse_rho)
#                             'n_pop': 50,            # Number of individuals in the population
#                             'n_obj': 2,             # Number of objectives to be minimized 
#                             'generations': 1000,    # Number of generations for the calibration algorithm
#                             })              

config = xr.Dataset(coords={'dt': 3,                # [hours]
                            'switch_alpha_ini': 0,  # Calibrate the initial position? (0: No, 1: Yes)
                            'Ysi': 1999,            # Initial year for calibration
                            'Msi': 1,               # Initial month for calibration
                            'Dsi': 1,               # Initial day for calibration
                            'Ysf': 2010,            # Final year for calibration
                            'Msf': 1,               # Final month for calibration
                            'Dsf': 1,               # Final day for calibration
                            'cal_alg': 'sceua',     # Avaliable methods: sceua
                            'metrics': 'mss',       # Metrics to be minimized (mss, RP, rmse, nsse)
                            'repetitions': 100000    # Number of repetitions for the calibration algorithm
                            })


wrkDir = os.getcwd()
config.to_netcdf(wrkDir+'/data_rot/config.nc', engine='netcdf4')

model = cal_Jaramillo21a(wrkDir+'/data_rot/')

setup = setup_spotpy(model)

results = setup.setup()

bestindex, bestobjf = spt.analyser.get_minlikeindex(results)
best_model_run = results[bestindex]
fields=[word for word in best_model_run.dtype.names if word.startswith('sim')]
best_simulation = list(best_model_run[fields])

a = best_model_run['para']
b = best_model_run['parb']
Lcw = best_model_run['parLcw']
Lccw = best_model_run['parLccw']

full_run, _ = jaramillo21a(model.P, model.Dir,model.dt, a, b, Lcw, Lccw, model.alpha_obs[0])

plt.rcParams.update({'font.family': 'serif'})
plt.rcParams.update({'font.size': 7})
plt.rcParams.update({'font.weight': 'bold'})
font = {'family': 'serif',
        'weight': 'bold',
        'size': 8}
fig = plt.figure(figsize=(12, 2), dpi=300, linewidth=5, edgecolor="#04253a")
ax = plt.subplot(1,1,1)
# ax.plot(best_simulation,color='black',linestyle='solid', label='Best objf.='+str(bestobjf))
ax.scatter(model.time_obs, model.alpha_obs,s = 1, c = 'grey', label = 'Observed data')
ax.plot(model.time, full_run, color='red',linestyle='solid', label= 'Jaramillo et al.(2021a)')
plt.fill([model.start_date, model.end_date, model.end_date, model.start_date], [-1e+5, -1e+5, 1e+5, 1e+5], 'k', alpha=0.1, edgecolor=None, label = 'Calibration Period')
plt.ylim([50, 60])
plt.xlim([model.time[0], model.time[-1]])
plt.ylabel('Shoreline orientation [m]', fontdict=font)
plt.legend(ncol = 6,prop={'size': 6}, loc = 'upper center', bbox_to_anchor=(0.5, 1.15))
plt.grid(visible=True, which='both', linestyle = '--', linewidth = 0.5)
fig.savefig('./results/Jaramillo21a_Best_modelrun_'+str(config.cal_alg.values)+'.png',dpi=300)

spt.analyser.plot_parametertrace(results)

config.close()