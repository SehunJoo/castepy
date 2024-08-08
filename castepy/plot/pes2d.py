#!/usr/bin/env python

import os
import sys

import pandas as pd                                                                                         
import numpy as np
import matplotlib.pyplot as plt

# 2-column fig with 3 plots
plt.rcParams.update({'font.size': 18})
#plt.rcParams.update({'font.size': 14})


def cryan2dat():                                                                                                
                                                                                                                    
    datafile = '2D_PES.dat'                                                                                         
                                                                                                                    
    if not os.path.isfile(datafile):                                                                                
        print(f"    generating {datafile} ...")                                                                     
        os.system(f"ca -l -nr -r 1>./{datafile} 2>/dev/null")                                                       
    else:                                                                                                           
        print(f"    {datafile} found ...")                                                                          
                                                                                                                    
    print("Done\n") 


def read_data():                                                                                                
                                                                                                                    
    datafile = '2D_PES.dat'                                                                                         
    a = []                                                                                                          
    b = []                                                                                                          
    energy = []                                                                                                     
                                                                                                                    
    with open(datafile, "r") as file:                                                                               
        for line in file:                                                                                           
            values = line.split()                                                                                   
            a.append(float(values[0].split("_")[-2])/1000)                                                          
            b.append(float(values[0].split("_")[-1])/1000)                                                          
            energy.append(float(values[3]) * float(values[6]))                                                      
                                                                                                                    
    d = {}                                                                                                          
    d['a'] = a                                                                                                      
    d['b'] = b                                                                                                      
    d['E(eV)'] = energy                                                                                             
                                                                                                                    
    df = pd.DataFrame(d)                                                                                            
    df = df.sort_values(by=['a', 'b'])                                                                              
    df['dE(eV)'] = df['E(eV)'] - df['E(eV)'].min()                                                                  
    print(df)                                                                                                       
                                                                                                                    
    return df      


def plot_scatter():                                                                                             
                                                                                                                    
    df = read_data()                                                                                           
                                                                                                                    
    x = df['a']                                                                                                     
    y = df['b']                                                                                                     
    de = df['dE(eV)']                                                                                               
                                                                                                                    
    fig, ax = plt.subplots()                                                                                        
    scatter = ax.scatter(x, y, c=de, cmap='viridis')                                                                
    cbar = plt.colorbar(scatter, ax=ax)                                                                             
    cbar.set_label(r'$\Delta$E (eV)', rotation=270, labelpad=20)                                                    
    cbar.ax.title.set_rotation(90)                                                                                  
    plt.xlabel('Displacement along a')                                                                              
    plt.ylabel('Displacement along b')                                                                              
    plt.savefig('2D_PES_plot_scatter.png', bbox_inches='tight')                                                                          
    plt.show()                                                                                                     
    plt.close(fig)                                                                                                  
                                                                                                                    
def plot_contourf():                                                                                            
                                                                                                                    
    df = read_data()                                                                                           
                                                                                                                    
    x = df['a']                                                                                                     
    y = df['b']                                                                                                     
    de = df['dE(eV)'] * 1000                                                                                              
                                                                                                                    
    X = df['a'].unique()                                                                                            
    Y = df['b'].unique()                                                                                            
    de_2d = de.values.reshape((len(Y), len(X)))                                                                     
                                                                                                                    
    fig, ax = plt.subplots()                                                                                        
    contour = ax.contourf(X, Y, de_2d.T, levels=20, cmap='viridis')                                                 

    # color bar
    cbar = plt.colorbar(contour, ax=ax)                                                                             
    cbar.set_label(r'$\Delta$E (meV)', rotation=270, labelpad=20)                                                    
    ticks = np.linspace(0, de.max(), 6)
    ticks = [int(tick) for tick in ticks]
    cbar.set_ticks(ticks)
    #tick_labels = [f'{tick:.1f}' for tick in ticks]
    #cbar.set_ticklabels(tick_labels)

    plt.xlabel('Displacement along a')                                                                              
    plt.ylabel('Displacement along b')                                                                              
    plt.savefig('2D_PES_plot_contourf.png', bbox_inches='tight')                                                                         
    plt.show()                                                                                                     
    plt.close(fig)          


cryan2dat()
plot_scatter()
plot_contourf()
