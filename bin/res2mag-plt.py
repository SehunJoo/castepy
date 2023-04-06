#!/usr/bin/env python

import matplotlib.pyplot as plt
import pandas as pd

df = pd.read_csv('df_mag.csv')
df = df.sort_values(by=['enthalpy'])
print(df.head())
df['enthalpy'] = df['enthalpy'] - df['enthalpy'].min()
#df = df.loc[df['enthalpy'] < 0.5]
print(df.head())
print(df.describe())

def plot(xcolumn, ycolumn, xlabel, ylabel, xlim=None, ylim=None):

    # plot for oxides containing two transition metals
    fig, ax = plt.subplots()
    
    x = df[xcolumn]
    y = df[ycolumn]
    
    # Set general font size
    fontsize=14
    plt.rcParams['font.size'] = fontsize
    
    # Set tick font size
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(fontsize)
    
    cmap='viridis'
    sc = ax.scatter(
        x,y,
        alpha=0.3,
        c=df['enthalpy'], cmap=cmap,
        #vmin=0, vmax=0.3,
    )
    
    ax.set_xlabel(xlabel, fontsize=fontsize)
    ax.set_ylabel(ylabel, fontsize=fontsize)
    if xlim != None:
        ax.set_xlim([-0.5,5.5])
    if ylim != None:
        ax.set_ylim([-0.5,5.5])
    
    # ax.xaxis
    # ax.xaxis.set_major_locator
    # ax.xaxis.set_major_formatter
    # ax.yaxis
    # ax.yaxis.set_major_locator
    # ax.yaxis.set_major_formatter
    
    #ax.legend()
    
    #ax.grid()
    
    cbar = fig.colorbar(
        sc, ax=ax,
        location='right', orientation='vertical'
    )
    
    cbar.set_label('Relative energy (eV/cell)', rotation=270, labelpad=20)
   
    if xlim != None or ylim != None:
        fig.savefig('magmom' + '_' +  xcolumn + '_' + ycolumn + '_lim' + '.png', bbox_inches='tight')
    else:
        fig.savefig('magmom' + '_' +  xcolumn + '_' + ycolumn +'.png', bbox_inches='tight')
    #plt.show()

df['spin'] = df['spin'].abs()
df['Co_spin'] = df['Co_spin'].abs()
df['Co_tet_spin'] = df['Co_tet_spin'].abs()
df['Co_oct_spin'] = df['Co_oct_spin'].abs()
df['Ni_spin'] = df['Ni_spin'].abs()

xcolumn='Ni_modspin'
ycolumn='Co_modspin'
xlabel="|$\mathit{\u03bc}_\mathrm{Ni}$|"
ylabel="|$\mathit{\u03bc}_\mathrm{Co}$|"
plot(xcolumn, ycolumn, xlabel, ylabel)
plot(xcolumn, ycolumn, xlabel, ylabel, xlim=[-0.5,5.5], ylim=[-0.5,5.5])

xcolumn='Co_tet_modspin'
ycolumn='Co_oct_modspin'
xlabel="|$\mathit{\u03bc}_\mathrm{Co_\mathrm{tet}}$|"
ylabel="|$\mathit{\u03bc}_\mathrm{Co_\mathrm{oct}}$|"
plot(xcolumn, ycolumn, xlabel, ylabel)
plot(xcolumn, ycolumn, xlabel, ylabel, xlim=[-0.5,5.5], ylim=[-0.5,5.5])

# magnetic ordering
df = df.loc[(df['enthalpy'] < 0.2)]

xcolumn='modspin'
ycolumn='spin'
xlabel="\u03A3|$\mathit{\u03bc}$|"
ylabel="|\u03A3$\mathit{\u03bc}$|"
plot(xcolumn, ycolumn, xlabel, ylabel)

xcolumn='Ni_modspin'
ycolumn='Ni_spin'
xlabel="|$\mathit{\u03bc}_\mathrm{Ni}$|"
ylabel="$\mathit{\u03bc}_\mathrm{Ni}$"
plot(xcolumn, ycolumn, xlabel, ylabel)
plot(xcolumn, ycolumn, xlabel, ylabel, xlim=[-0.5,5.5], ylim=[-0.5,5.5])

xcolumn='Co_modspin'
ycolumn='Co_spin'
xlabel="|$\mathit{\u03bc}_\mathrm{Co}$|"
ylabel="$\mathit{\u03bc}_\mathrm{Co}$"
plot(xcolumn, ycolumn, xlabel, ylabel)
plot(xcolumn, ycolumn, xlabel, ylabel, xlim=[-0.5,5.5], ylim=[-0.5,5.5])

xcolumn='Co_tet_modspin'
ycolumn='Co_tet_spin'
xlabel="|$\mathit{\u03bc}_\mathrm{Co_\mathrm{tet}}$|"
ylabel="$\mathit{\u03bc}_\mathrm{Co_\mathrm{tet}}$"
plot(xcolumn, ycolumn, xlabel, ylabel)
plot(xcolumn, ycolumn, xlabel, ylabel, xlim=[-0.5,5.5], ylim=[-0.5,5.5])

xcolumn='Co_oct_modspin'
ycolumn='Co_oct_spin'
xlabel="|$\mathit{\u03bc}_\mathrm{Co_\mathrm{oct}}$|"
ylabel="$\mathit{\u03bc}_\mathrm{Co_\mathrm{oct}}$"
plot(xcolumn, ycolumn, xlabel, ylabel)
plot(xcolumn, ycolumn, xlabel, ylabel, xlim=[-0.5,5.5], ylim=[-0.5,5.5])
