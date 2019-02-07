import os
import numpy as np
import matplotlib.pyplot as plt
#  import uncertainties.unumpy as unp
#  from uncertainties.unumpy import nominal_values as noms
#  from uncertainties.unumpy import std_devs as stds
#  from uncertainties import ufloat
#  from scipy.optimize import curve_fit
#  import scipy.constants as const
#  import imageio
#  from scipy.signal import find_peaks
#  import pint
import pandas as pd
from tab2tex import make_table
#  ureg = pint.UnitRegistry(auto_reduce_dimensions = True)
#  Q_ = ureg.Quantity
tugreen = '#80BA26'

#  c = Q_(const.value('speed of light in vacuum'), const.unit('speed of light in vacuum'))
#  h = Q_(const.value('Planck constant'), const.unit('Planck constant'))
#  c = const.c
#  h = const.h
#  muB = const.value('Bohr magneton')


def linear(x, a, b):
    '''Lineare Regressionsfunktion'''
    return a * x + b

def ui_characteristic():
    '''Strom-Spannungs-Kennlinie'''
    U, I = np.genfromtxt('rohdaten/ui-characteristic.txt', unpack=True)

    print('\tPlot UI-Characteristic')
    plt.axvspan(xmin=65, xmax=85, facecolor=tugreen, label=r'Mögliches $U_{\mathrm{Dep}}$')  # alpha=0.9
    plt.axvline(x=100, color='k', linestyle='--', linewidth=0.8, label=r'Anglegte $U_{\mathrm{Exp}}$')
    plt.plot(U, I, 'kx', label='Messwerte')
    plt.xlabel(r'$U\:/\:\si{\volt}$')
    plt.ylabel(r'$I\:/\:\si{\micro\ampere}$')
    plt.legend(loc='lower right')  # lower right oder best
    plt.tight_layout()
    plt.savefig('build/ui-characteristic.pdf')
    plt.clf()

    mid = len(U) // 2  # use modulo operator
    make_table(header= ['$U$ / \\volt', '$I$ / \\micro\\ampere', '$U$ / \\volt', '$I$ / \\micro\\ampere'],
            places= [3.0, 1.2, 3.0, 1.2],
            data = [U[:mid], I[:mid], U[mid:], I[mid:]],
            caption = 'Aufgenommene Strom-Spannungs-Kennlinie.',
            label = 'tab:ui-characteristic',
            filename = 'build/ui-characteristic.tex')


def pedestal_run():
    '''Auswertung des Pedestals, Noise und Common Mode'''
    # adc counts
    adc = np.genfromtxt('rohdaten/Pedestal.txt',
            unpack=True,
            delimiter=';')
    # pedestal, mean of adc counts without external source
    pedestal = np.mean(adc, axis=0)
    # common mode shift, global noise during a measurement
    common_mode = np.mean(adc-pedestal, axis=1)
    # temporary variable to compute adc - pedestal - common_mode
    difference = ((adc - pedestal).T - common_mode).T
    # noise, the 'signal' of the measurement without ext source
    noise = np.sqrt(np.sum((difference)**2, axis=0)/(len(adc)-1))

    print('\tPlot Pedestal and Noise')
    stripe_indices = np.array(range(128))
    fig, ax1 = plt.subplots()
    #  plt.bar(stripe_indices,
            #  height = pedestal,
            #  width = 0.8)
    ax1.errorbar(x=stripe_indices,
            y=pedestal,
            xerr=0.5,
            yerr=0.2,
            elinewidth=0.7,
            fmt='none',
            color='k',
            label='Pedestal')
    ax1.set_ylabel(r'Pedestal\:/\:ADCC', color='k')
    ax1.set_xlabel('Kanal')
    ax1.tick_params('y', colors='k')
    ax1.set_ylim(500.5, 518.5)
    ax2 = ax1.twinx()
    ax2.errorbar(x=stripe_indices,
            y=noise,
            xerr=0.5,
            yerr=0.01,
            elinewidth=0.7,
            fmt='none',
            color=tugreen,
            label='Noise')
    ax2.set_ylabel(r'Noise\:/\:ADCC', color=tugreen)
    ax2.tick_params('y', colors=tugreen)
    ax2.set_ylim(1.75, 2.55)
    #  fig.legend()
    fig.tight_layout()
    fig.savefig('build/pedestal.pdf')
    fig.clf()

    print('\tPlot Common Mode Shift')
    plt.hist(common_mode, histtype='step', bins=30, color='k')
    plt.xlabel('Common Mode Shift\:/\:ADCC')
    plt.ylabel('Anzahl Messungen')
    plt.tight_layout()
    plt.savefig('build/common-mode.pdf')
    plt.clf()


def kalibration():
    '''Kalibration zur Umrechnung ADC Counts in Energie'''
    print('\tPlot Delay Scan')
    #  delay, y = np.genfromtxt('rohdaten/Delay_Scan', unpack=True)
    df_delay = pd.read_table('rohdaten/Delay_Scan', skiprows=1, decimal=',')
    df_delay.columns = ['delay', 'adc']
    best_delay_index = df_delay['adc'].idxmax(axis=0)
    print('\tBest Delay at {} ns'.format(df_delay['delay'][best_delay_index]))
    plt.bar(df_delay['delay'].drop(index=best_delay_index),
            df_delay['adc'].drop(index=best_delay_index), color='k')
    plt.bar(df_delay['delay'][best_delay_index], df_delay['adc'][best_delay_index],
            color=tugreen, label='Maximum')
    plt.xlabel(r'Delay\:/\:\si{\nano\second}')
    plt.ylabel('Durchschnittliche ADC Counts')
    plt.legend(loc='upper right')
    plt.tight_layout()
    plt.savefig('build/delay-scan.pdf')
    plt.clf()

    print('\tCompute Kalibration')
    # Energie zur Erzeugung eines Elektron-Loch-Paares in Silizium in eV
    energy_eh_couple = 3.6
    # Importiere Kalibrationsmessungen der Channel 10, 35, 60, 90, 120
    channel_indices = [10, 35, 60, 90, 120]
    channel_dict = {}  # Dictionary mit den vermessenen Kanälen
    for index, channel in enumerate(channel_indices):
        #  plt.subplot(2, 2, index+1, sharex=ax_1)
        channel_dict['{}'.format(channel)] = pd.read_table(
                'rohdaten/Calib/channel_{}.txt'.format(channel),
                skiprows=1, decimal=',')
        channel_dict['{}'.format(channel)].columns = ['pulse', 'adc']
        # transform pulse to injected eV
        channel_dict['{}'.format(channel)]['pulse'] *= energy_eh_couple
    print('NOCH NICHT FERTIG!')
    # TODO: Über alle channel_indices mitteln und Polynom fitten
    # TODO: Gemittelte Kurve darstellen zusammen mit Fit

    print('\tPlot Kalibration')
    plt.subplots(2, 2, sharex=True, sharey=True)
    ax_1 = plt.subplot(2, 2, 1)
    ax_2 = plt.subplot(2, 2, 2)
    ax_3 = plt.subplot(2, 2, 3, sharex=ax_1)
    ax_4 = plt.subplot(2, 2, 4, sharex=ax_2)
    ax_1.plot(channel_dict['10']['pulse'], channel_dict['10']['adc'], 'k-', label='Kanal 10')
    ax_2.plot(channel_dict['35']['pulse'], channel_dict['35']['adc'], 'k-', label='Kanal 35')
    ax_3.plot(channel_dict['90']['pulse'], channel_dict['90']['adc'], 'k-', label='Kanal 90')
    ax_4.plot(channel_dict['120']['pulse'], channel_dict['120']['adc'], 'k-', label='Kanal 120')
    ax_1.legend(loc='lower right')
    ax_2.legend(loc='lower right')
    ax_3.legend(loc='lower right')
    ax_4.legend(loc='lower right')
    ax_1.set_ylabel('ADCC')
    ax_3.set_ylabel('ADCC')
    ax_3.set_xlabel(r'Injizierte Energie$\:/\:$\si{\electronvolt}')
    ax_4.set_xlabel(r'Injizierte Energie$\:/\:$\si{\electronvolt}')
    plt.tight_layout()
    plt.savefig('build/calibration.pdf')
    plt.clf()

    print('\tPlot Vergleich')
    channel_dict['vgl'] = pd.read_table('rohdaten/Calib/channel_60_null_volt.txt',
            skiprows=1, decimal=',')
    channel_dict['vgl'].columns = ['pulse', 'adc']
    channel_dict['vgl']['pulse'] *= energy_eh_couple
    plt.plot(channel_dict['60']['pulse'], channel_dict['60']['adc'], 'k-', label=r'\SI{100}{\volt}')
    plt.plot(channel_dict['vgl']['pulse'], channel_dict['vgl']['adc'], color=tugreen, label=r'\SI{0}{\volt}')
    plt.xlabel(r'Injizierte Energie$\:/\:$\si{\electronvolt}')
    plt.ylabel('ADCC')
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig('build/vergleich.pdf')
    plt.clf()



# Alte Funktion, hier nur syntax klauen
def eichung():
    '''Eichung der Magnetischen Flussdichte'''
    # Eichung des Elektromagneten
    I, B = np.genfromtxt('rohdaten/eichung.txt', unpack=True)
    params, covariance = curve_fit(eichfunktion, I, B)
    errors = np.sqrt(np.diag(covariance))
    print('Eichung')
    print(f'\ta_0 = {params[0]} ± {errors[0]}')
    print(f'\ta_1 = {params[1]} ± {errors[1]}')
    print(f'\ta_2 = {params[2]} ± {errors[2]}')
    print(f'\ta_3 = {params[3]} ± {errors[3]}')
    print(f'\ta_4 = {params[4]} ± {errors[4]}')

    # Plot
    x_plot = np.linspace(0, 20, 10000)
    plt.plot(I, B, 'kx', label='Messwerte')
    plt.plot(x_plot, eichfunktion(x_plot, *params), 'b-', label='Regression')
    plt.xlabel(r'$I\:/\:$A')
    plt.ylabel(r'$B\:/\:$mT')
    plt.tight_layout()
    plt.savefig('build/eichung.pdf')
    plt.clf()

    I_halb = len(I) // 2
    B_halb = len(B) // 2
    # Speichern der Messwerte
    make_table(header= ['$I$ / \\ampere', '$B$ / \milli\\tesla', '$I$ / \\ampere', '$B$ / \milli\\tesla'],
            places= [2.1, 4.0, 2.1, 4.0],
            data = [I[:I_halb], B[:B_halb], I[I_halb:], B[B_halb:]],
            caption = 'Magnetische Flussdichte in Abhängigkeit des angelegten Stroms.',
            label = 'tab:eichung',
            filename = 'build/eichung.tex')
    return params, errors


if __name__ == '__main__':

    if not os.path.isdir('build'):
        os.mkdir('build')

    print('UI-Characteristic')
    ui_characteristic()
    print('Pedestal Run')
    pedestal_run()
    print('Kalibration')
    kalibration()
