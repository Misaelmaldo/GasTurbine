import numpy as np
import math
import matplotlib.pyplot as plot
import pandas as pd



# Si la Data tiene comentario es por ser verificada, de no llevar comentario no tengo referencias de data del motor o de las formulas
############################################### F-135-100 DATA ################################################
### INITIAL CONDITIONS ######
M = 1.2                              #Mach number                DECIDIR
Ta = 215                             #Ambient Temperature (K)    DECIDIR
Pa = 22                              #Ambient Pressure    (KPa)  DECIDIR
R = 0.287                            #Ideal Gas Constant (KJ/kg*K)
Kc = 1.4                             #Specific Heat ratio Cold air
C = np.sqrt(Kc * 1000 * R * Ta)      #Sound velocity Formula (m/s)
U = M * C                            #Velocity from Mach number Formula (m/s)
### INLET ####
eta_d = 0.98                         #Diffusser Eficiency BUSCAR
Ain = 1.063                          #Area Inlet (m^2) CALCULADO
#### FAN #####
BPR = 0.57                           #Bypass Ratio EDITED
eta_F = 0.90                         #Fan Efficiency EDITED
F_PR = 4.7                           #Fan Pressure Ratio Added
#### HPC #####
OPR = 28.2                           #Overall Pressure Ratio EDITED
HPC_PR = 6.144                       #High-Compressor Pressure Ratio EDITED
eta_HPC = 0.85                       #Isent. effic. high-pressure compressor EDITED
#### Combustor Chamber ########################################################################
Qr = 48000                            #INVESTIGAR FUEL KJ/kg
Kh = 1.3                              #Sigma hot Specific Heat Ratio
Cpc = 1.005                            #Constant Specific Heat cold (KJ/(Kg*K))
Cph = 1.148                            #Constant Specific Heat hot  (KJ/(Kg*K))
dPcc = 0.005                           #Delta Pressurer  CC
CC_PR = 0.995                          #Combuster Pressure ratio
eta_b = 0.99                           #Burner eff
TIT = 2255                           #High-Pressure Turbine Inlet Temperature EDITED
#### HPT ###########################################################################################
eta_HPT = 0.90                       #Isent. effic. High-Pressure Turbine EDITED
mech_eff_1 = 0.9                     #Mechanical efficiency of HP-Spool
#### LPT ###########################################################################################
eta_LPT = 0.91                       #Isent. effic. Low-Pressure Turbine EDITED
mech_eff_2 = 0.90                     #Mechanical efficiency of LP-Spool
#### Mixer ##########################################################################################
dPmix = 0                            #Pressure drop at mixer
### Nozzle ########################################################################################
Ae = 1.3                               #Area  Exhaust    FALTA
eta_N = 0.99                         #Nozzle Efficiency Assumed from Thesis
_TSFC= {}
_ST= {}
######################################### Thermodinamic Analysis Model ########################################
################################################## INLET 01-02 ###############################################
T_2 = Ta * (1 + ((Kc - 1) / 2) * M ** 2)                                                                   #verified
P_2 = Pa * (1 + eta_d * ((Kc - 1) / 2) * M ** 2) ** (Kc / (Kc - 1))                                                #verified
##################################################### FAN 02-03 ################################################
P_3 = P_2 * F_PR                                                                                           #verified
T_3 = T_2 * (1 + (F_PR ** ((Kc - 1) / Kc) - 1) / eta_F)                                                    #verified
########################################### HIGH PRESSURE COMPRESSOR 03-04 #####################################
P_4 = P_3 * HPC_PR                                                                                         #verified
T_4 = T_3 * (1 + ((HPC_PR ** ((Kc - 1) / Kc) - 1)) / eta_HPC)                                              #verified
################################################## COMBUSTOR 04-05 #############################################
P_5 = P_4 * CC_PR                                                                                       #veried
T_5 = TIT                                                                                                  #verified Given data
f = ((Cph * T_5) - (Cpc * T_4)) / ((eta_b * Qr) - (Cph * T_5))                                             #Fuel-to-air ratio
########################################### HIGH-PRESSURE TURBINE (HPT) 05-06 ###################################
T_6 = (T_5 - ((Cpc * (T_4 - T_3)) / (Cph * (1 + f))))                                                      #verified
P_6 = P_5 * (1 - (1 / eta_HPT) * (1 - (T_6 / T_5))) ** (Kh / (Kh - 1))                                     #verified
########################################### LOW-PRESSURE TURBINE (LPT) 06-07 ####################################
T_7 = T_6 - ((Cpc * (1 + BPR) * (T_3 - T_2)) / (Cph * (1 + f))) - ((Cpc * (T_4 - T_3)) / (Cph * (1 + f)))  #verified
P_7 = P_6 * (1 - (1 / eta_F) * (1 - (T_7 / T_6))) ** (Kh / (Kh - 1))                                       #verified
#################################################### MIXER 07-08 ################################################
T_8 = (BPR * Cpc * T_3 + (1+f) * Cph * T_7) / ((1 + BPR + f) * Cph)                                            #verified
P_8 = P_7 * (1 - dPmix)                                                                                        #verified Chapter 5.5
################################################# EXHAUST NOZZLE 08-09 ###########################################
P_cr = P_8 * (1 - (1 / eta_N) * ((Kh - 1) / (Kh + 1))) ** (Kh / (Kh - 1))                                #verified
if P_cr >= Pa:
 P_9 = P_cr                                                                                                #Choked
 T_9 = (2 * T_8) / (Kh + 1)                                                                                #verified
 V_9 = np.sqrt(Kh * R * 1000 * T_9)                                                                               #verified
 print('CHOKED EXHAUST NOZZLE')
else:
 print('UNCHOKED EXHAUST NOZZLE')
 P_9 = Pa
 T_9 = T_8 * (1 - eta_N * (1 - (P_9 / P_8) ** ((Kh - 1) / (Kh))))                                           #verified
 V_9 = np.sqrt(2 * Cph * (T_8 - T_9))                                                                       #verified
#############################################  Performance Parameters ####################################################
m_a = (Pa  * U / (R * Ta) ) * Ain                                                                          # mass flow rate of air
T = ((m_a * ((1 + f)* V_9 - U)) / 1000) + Ae * (P_9 - Pa)                                                  # Thrust (KN)
ST = (T / m_a) * 1000                                                                                      # Specific Thrust (N/Kg/s)
m_f = f * m_a                                                                                              # fuel mass flow rate
TSFC = m_f / T                                                                                             # thrust specific fuel consumption
eta_p = (ST * U) / (ST * U + (0.5 * (1 + f) / (BPR + 1)) * (V_9 - U) ** 2 + (0.5 * (BPR / (BPR + 1)) * (V_9 - U) ** 2)) # propulsive efficiency
eta_th = (ST * U + (0.5 * (1 + f) / (BPR + 1)) * (V_9 - U) ** 2 + 0.5 * (BPR / (BPR + 1)) * (V_9 - U) ** 2) / ((f / (BPR + 1)) * (Qr * 1000)) #Thermal efficiency
eta_o = eta_th * eta_p  # overall efficiency
fuel_consumption = m_f * 3.6  # fuel consumption ton/h
####################################### Outputs of desired parameters ############################################
print('-------------------------Results----------------------------\n')
print('Flight Velocity: {} m/s\n'.format(U));
print('Sound Speed: {} m/s\n'.format(C));
print('Specific Thrust: {} N-s/kg\n'.format(ST));
print('Thrust Specific Fuel Consumption: {} kg/N-s\n'.format(TSFC));
print('Thrust: %f KN' % T);
print('Fuel mass flow: %f' % m_f);
print('Fuel to air ratio: %f' % f);
print('Propulsive Efficiency: %f %%' % (eta_p * 100));
print('Thermal Efficiency: %f %%' % (eta_th * 100));
print('Overall Efficiency: %f %%' % (eta_o * 100));
print('V_09: %f m/s' % V_9);
print('T_09: %f K' % T_9);
print('P_08: %f KPa' % P_8);
print('P_09: %f KPa' % P_9);
print('Air Mass Flow Rate: %f kg/s' % m_a)
################# Stations Data  ###############
# Replace these placeholders with the actual calculations for your engine
stages = ['01', '02', '03', '04', '05', '06', '07', '08', '09']
temperatures = [Ta, T_2, T_3, T_4, T_5, T_6, T_7, T_8, T_9]  # Replace with temperature calculations
pressures = [Pa, P_2, P_3, P_4, P_5, P_6, P_7, P_8, P_9]     # Replace with pressure calculations

# Create a DataFrame and set "Stage" as the index
data = {'Temperature (K)': temperatures, 'Pressure (KPa)': pressures}
df = pd.DataFrame(data, index=stages)
df.index.name = 'Stage'  # Remove the index name
print(df)
