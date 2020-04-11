import requests
import pandas as pd
import time
from datetime import datetime
import matplotlib.pyplot as plt
from  matplotlib.ticker import MaxNLocator
import seaborn as sns


"""
A data loader for the XRP Ledger WebSocket API.
"""
class XRPLedgerWebSocketAPI(object):
    url = ""
    
    #XRPLedgerWebSocketAPI has a parameterized constructor
    def __init__(self, url):
        self.url = url
    
    
    def getRequest(self, payload):
        """
        getRequest excutes the equivalent of a cURL request, for example:
        
        curl -H 'Content-Type: application/json' 
            -d '{"method":"server_info","params":[{}]}' 
            https://s1.ripple.com:51234/
        """
        headers = {'content-type': 'application/json'}        
        return requests.get(self.url, data=payload, headers=headers)


    def getServerInfoLedgerCloseFrequency(self, iterations, sample_frequency):
        """
        getServerInfoLedgerCloseFrequency data from XRPLedger WebSocket API.

        :returns a panadas dataframe 
                 'Index' - index for ordering the sequence 
                 'Closed Ledgers' - number of closed ledgers in the sample
                 'Duration' - datetime of the duration of the sample
                 'TimeStamp' - string representaion of the sample time
                 'Average Ledger Close' - average of closed ledgers inferred from the sample
                 'Last Ledger Close' - XRPLedger last_close converge_time_s
                 'Proposers' - XRPLedger last_close proposers
        """
        #######################################################################
        #Initialise our connection by extracting the first sample.
        #Request server info from XRPLedger WebSocket API
        #######################################################################
        payload = '{"method":"server_info","params":[{}]}'
        r = self.getRequest(payload)
        
        #Unpack the server info JSON object 
        json_array = r.json()        
        result = json_array['result']
        info = result['info']

        #SEQUENCE NUMBER
        validated_ledger = info['validated_ledger']
        seq = validated_ledger['seq']
        
        #Initialise the previous sequence number for use in the for loop
        previous_seq = int(seq)
        cumulative_seq = 0
        #######################################################################

        #######################################################################
        #Loop through the number of samples calculating the number of closed 
        #ledgers ('Closed Ledgers') and elapsed time per sample ('Duration') 
        #######################################################################
        results_list = []
        for i in range(iterations):
            time.sleep(sample_frequency) #Sleep for sample frequency time (in seconds)
                
            r = self.getRequest(payload) #Get the next sever_info json object
        
            json_array = r.json() #Unpack the server_info json objet

            #Navigate the server_info json object to extract required data
            result = json_array['result']
            info = result['info']
        
            last_close = info['last_close']
            converge_time_s = last_close['converge_time_s'] #Extract last ledger close duration
            proposers = last_close['proposers'] #Extract number of proposers
        
            xrp_time = info['time'] #Extract time and convert to Python time object
            xrp_date_time_now = datetime.strptime(xrp_time, '%Y-%b-%d %H:%M:%S.%f UTC')
   
            #Extract the ledger sequence number
            validated_ledger = info['validated_ledger']
            seq = validated_ledger['seq']            
            seq_diff = int(seq) - previous_seq #Closes in this sample period
            cumulative_seq += seq_diff #Keep a cumulative running total
            
            #Create the result
            new_result = []
            new_result.append(i)     
            new_result.append(seq_diff)
            new_result.append(cumulative_seq)
            new_result.append(xrp_date_time_now.strftime("%H:%M:%S"))
            new_result.append(converge_time_s)
            new_result.append(proposers)
            results_list.append(new_result)
            print(new_result);
            
            previous_seq = int(seq)
        #######################################################################
        
        #######################################################################
        #Create the results pandas DataFrame
        #######################################################################
        results = pd.DataFrame(results_list, columns = ['Index', 
                                     'Closed Ledgers per Sample', 'Cumulative Closed Ledgers',
                                     'SamplingFrequency', 'Last Ledger Close', 'Proposers'])
        #######################################################################
        
        #######################################################################
        #Return the pandas dataframe
        #######################################################################
        return results



if __name__ == '__main__':  
    ###########################################################################
    #Initialise our XRP Ledger
    ###########################################################################
    url = 'https://s1.ripple.com:51234/'
    source = XRPLedgerWebSocketAPI(url)
    ###########################################################################
    
    ###########################################################################
    #Call getServerInfoLedgerCloseFrequency to extract the ledger close data
    ###########################################################################
    iterations = 22
    sample_frequency = 3.03
    results = source.getServerInfoLedgerCloseFrequency(iterations, sample_frequency)
    ###########################################################################
    
    ###########################################################################
    #Store the results as a CSV
    ###########################################################################
    filename='XRPLedger_ServerInfoLedgerCloseFrequency.csv'
    results.to_csv(filename, index=False)
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
    title = "Timeseries Sampling of XRP Ledger Closes (Samping every " + str(sample_frequency) + " seconds)"
    plt.title(title, fontsize= 15)
    ax = sns.barplot(x='SamplingFrequency', y='Closed Ledgers per Sample', data=results)
    
    #Add a cumulative lineplot with separate y axis, on the right hand side of the plot
    ax2 = ax.twinx()
    ax2.yaxis.set_major_locator(MaxNLocator(integer=True))
    sns.lineplot(x='SamplingFrequency', y='Cumulative Closed Ledgers', data=results, ax=ax2)
    
    plt.show(sns)
    ###########################################################################



