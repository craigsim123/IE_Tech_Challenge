import pandas as pd
import matplotlib.pyplot as plt
from  matplotlib.ticker import MaxNLocator
import seaborn as sns

"""
This Python script will recreate the visualisation of the data within the 
XRPLedger_ServerInfoLedgerCloseFrequency.csv results file

NOTE: This file can only be run after ripple.py has been run and has successfully
created the file XRPLedger_ServerInfoLedgerCloseFrequency.csv
"""
if __name__ == '__main__':  
    ###########################################################################
    #Load the results from the CSV
    ###########################################################################
    filename='XRPLedger_ServerInfoLedgerCloseFrequency.csv'
    results = pd.read_csv(filename)
    ###########################################################################
    
    ###########################################################################
    #Drop the results where there were no closes within the sample period as
    #this will give incorrect statistics by double counting previous closes
    ###########################################################################
    stats_results = results.copy() #Deep copy, ok as we're looking at small data volumes in this example
    stats_results.drop( stats_results[ stats_results['Closed Ledgers per Sample'] == 0 ].index , inplace=True)
    legend = stats_results["Last Ledger Close"].describe().to_string()
    legend = "Ledger Close Stats\n(Converge Time)\n" + legend
    print(legend);
    ###########################################################################
    
    ###########################################################################
    #Create a timeseries barplot and lineplot to analyse the close frequency
    ###########################################################################
    sns.set_context("notebook", font_scale=0.9, rc={"lines.linewidth": 2.5})
    plt.figure(figsize=(16, 6))
    plt.xticks(rotation=45, horizontalalignment='right')
    plt.gca().yaxis.set_major_locator(MaxNLocator(integer=True))
    plt.legend(title=legend, loc='upper left')
    title = "Timeseries Sampling of XRP Ledger Closes"
    plt.title(title, fontsize= 15)
    ax = sns.barplot(x='SamplingFrequency', y='Closed Ledgers per Sample', data=results)
    
    #Add a cumulative lineplot with separate y axis, on the right hand side of the plot
    ax2 = ax.twinx()
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    sns.lineplot(x='SamplingFrequency', y='Cumulative Closed Ledgers', data=results, ax=ax2)
    
    plt.show(sns)
    ###########################################################################



