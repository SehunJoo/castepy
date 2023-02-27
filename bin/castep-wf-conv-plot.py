#!/usr/bin/env python

import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as colors
import matplotlib.ticker as tick
import pandas as pd
import numpy as np

ylim = [];
ylim = [-437.385, -437.378]

def main():

    df = pd.read_csv("castep-conv.csv")
    print(df)
    

    # filter data
    df = df.loc[df[col_cut] >= 800]
    #df = df.loc[df[col_fgs] >= 2.0]
    #print(df)


    # plot energy vs fgs for same cutoff
    plot_e_fgs(df=df)
    plot_e_cut(df=df)


def plot_e_fgs(df=None):

    print('plot energy vs fine grid scale for different cutoff energy...')

    # data preprocessing
    nlines = len(df[col_cut].unique())
    
    # plot variables
    cm = 1/2.54
    cmap = mpl.colormaps['Spectral']
    colors = cmap(np.linspace(0, 1, nlines))

    plt.rc('font', size=14)
    plt.rc('figure', figsize=(14*cm, 14/1.24*cm))
    plt.rc('lines', marker='o', markersize=4, linestyle='solid', linewidth=1)
    plt.rc('legend', frameon=False)
    
    # create figure and axes
    fig, ax = plt.subplots()

    # plot lines
    for i, cut in enumerate(df[col_cut].unique()):
        print('    ' + 'plot line - cutoff energy : ', cut)
        df_cut = df.loc[df[col_cut] == cut]
        ax.plot(df_cut[col_fgs], df_cut[col_e], label=cut, color=colors[i])
    
    if len(ylim) == 2:
        ax.set_ylim(ylim)

    # axes label
    ax.set_xlabel('Fine grid scale')
    ax.set_ylabel('Energy (eV/atom)')

    # axes tick - format of ticklabel
    ax.xaxis.set_major_formatter(tick.FormatStrFormatter('%.1f'))
    ax.yaxis.set_major_formatter(tick.FormatStrFormatter('%.3f'))


    ax.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=10)

    fig.savefig("castep-conv-e-fgs.png", bbox_inches="tight")


def plot_e_cut(df):

    print('plot energy vs cutoff for different fine grid scale...') 

    # data preprocessing
    nlines = len(df[col_fgs].unique())

    # plot variables
    cm = 1/2.54
    cmap = mpl.colormaps['Spectral']
    colors = cmap(np.linspace(0, 1, nlines))

    plt.rc('font', size=14)
    plt.rc('figure', figsize=(14*cm, 14/1.24*cm))
    plt.rc('lines', marker='o', markersize=4, linestyle='solid', linewidth=1)
    plt.rc('legend', frameon=False)

    # create figure and axes
    fig, ax = plt.subplots()

    # plot lines
    for i, fgs in enumerate(df[col_fgs].unique()):
        print('    ' + 'plot line - find grid scale : ', fgs)
        df_fgs = df.loc[df[col_fgs] == fgs]
        ax.plot(df_fgs[col_cut], df_fgs[col_e], label=fgs, color=colors[i])
    
    if len(ylim) == 2:
        ax.set_ylim(ylim)

    # axes label
    ax.set_xlabel('Cutoff energy (eV)')
    ax.set_ylabel('Energy (eV/atom)')

    # axes tick - format of ticklabel
    ax.xaxis.set_major_formatter(tick.FormatStrFormatter('%.0f'))
    ax.yaxis.set_major_formatter(tick.FormatStrFormatter('%.3f'))

    ax.legend(loc="center left", bbox_to_anchor=(1.05, 0.5), fontsize=10)

    fig.savefig("castep-conv-e-cut.png", bbox_inches="tight")

    


def plot_2d():
    print('minimum cutoff:',df[colcut].min())
    print('maximum cutoff:',df[colcut].max())
    
    #df = df.loc[df[cut] >= 350]
    
    colx = 'cutoff_energy(eV)'
    coly = 'fine_grid_scale'
    colz = 'energy(eV/atom)'
    
    df = df.pivot(columns=colx, index=coly, values=colz)
    print(df)
    
    X = df.columns.values
    Y = df.index.values
    Z = df.values
    #print(X)
    #print(Y)
    #print(Z)
    x,y=np.meshgrid(X,Y)
    Z = (Z-Z.min()) * 1000
    #print(x)
    #print(y)
    
    
    
    
    fig, ax = plt.subplots()
    
    fig.set_size_inches(14*cm, 14/1.24*cm)
    
    ax.set_xlabel('Cutoff energy (eV)', fontsize=fontsize)
    ax.set_ylabel('Fine grid scale', fontsize=fontsize)
    
    
    # colors
    cmap = plt.colormaps['Spectral_r']
    
    # normalization
    norm = colors.LogNorm(vmin=0.1, vmax=10, clip='True')
    #norm = colors.CenteredNorm(vcenter=eref)
    
    #ax.contourf(x,y,Z, cmap="Spectral_r")
    plot = ax.pcolormesh(x,y,Z, cmap=cmap, norm=norm)
    #ax.pcolormesh(x,y,Z, cmap="Spectral_r", norm=colors.LogNorm(vmin=0.1, vmax=10))
    
    # colorbar
    cbar = plt.colorbar(plot,ax=ax) 


##################################################
# Main
##################################################

if __name__ == '__main__':

    # global variables
    
    col_e= 'energy(eV/atom)'
    col_cut = 'cutoff_energy(eV)'
    col_fgs = 'fine_grid_scale'
    col_gs = 'grid_scale'

    main()

