import matplotlib.pylab as plt
from matplotlib.ticker import ScalarFormatter
from collections import OrderedDict
import os
from textwrap import wrap
import sys
import csv
MASTER_PORT = "port11"
MASTER_HOSTNAME = "elf-cluster"

#colours to use for the graphs
colours = ["#e6194b","#3cb44b","#ffe119", "#f58231", "#911eb4", "#46f0f0", "#000080", "#aa6e28", "#800000", "#808080", "#fabebe"]

"""
Read in the csv. This returns an ordered dict 
with an entry for each port/node. Each value contains a list 
of measurements associated with that port/node. 
The convert_to_bits param is an option on whether the 
measurement should be converted to megabits per second. 
"""
def read_csv(filename, is_port_data, convert_to_bits=False):
    data = dict()
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if is_port_data:

                value = float(row["derivative"])
                if convert_to_bits: 
                    value = (value*8)/1000000 #byte/sec to megabit/sec
            else:
                value = float(row["value"])

            value_list = data.get(row["tags"])
            if value_list is None:
                value_list = []
                data[row["tags"]] = value_list
            value_list.append(value)

    alphabetical_data = OrderedDict()
    if is_port_data:
        alphabetical_data[MASTER_PORT] = data.pop(MASTER_PORT)
    else:
        alphabetical_data[MASTER_HOSTNAME] = data.pop(MASTER_HOSTNAME)

    for key, value in sorted(data.items()):
        alphabetical_data[key] = value
    return alphabetical_data

"""
Creates tick labels from the range 0 - max * 10.
This is because the x axis represents the time elapsed and 
measurements are collected every 10 seconds. So between each
adjacent measurement is 10 seconds
"""
def create_x_axis_tick_labels(max):
    x_axis = []
    for i in range(0,max):
            x_axis.append(i*10)
    return x_axis

"""
Generates the number of rows and columns to be used by the subplot
Maximum number of columns is 5
"""
def generate_subplot_dimension(total_size):
    #see if it is divisible by numbers from 5-2
    for i in range(5,1,-1):
        if total_size % i == 0:
            return (total_size/i, i)

    #not divisible
    return ((total_size/2)+1, 2)

"""
Create a graph from the data given. Each element in the data represents 
a subplot in the graph. The graph will be titled with the param: graph_title
and label the y axis with the param: y axis label. Finally, it will be saved
as a png file named with the param: graph_filename.
"""
def plot_all(data, graph_title, y_axis_label, graph_filename, is_port_data, max_y):

    #how many rows and columns to use for the subplots
    dimension = generate_subplot_dimension(len(data))
    #generate the subplots. The figsize is the width and height of the whole graph in inches
    fig, axlist = plt.subplots(dimension[0], dimension[1], figsize = (dimension[1]*4,dimension[0]*4))
    #the original axlist is a list of lists. This coverts it to just a list
    axlist = axlist.flatten()

    #check that there aren't going to be any empty subplots
    difference =  (dimension[0] * dimension[1]) - len(data)
    #if there are empty subplots, reduce the number of subplots
    for count in range(difference,0, -1):
        fig.delaxes(axlist[0])

    #update the ax list in case we deleted some subplots
    axlist = fig.axes

    #dont use scientific notation
    y_formatter = ScalarFormatter(useOffset=False)
    y_formatter.set_scientific(False)
    
    i = 0
    for d in data:
        #get a subplot to draw in
        ax = axlist[i]
        #set y axis to not use scientific notation
        ax.yaxis.set_major_formatter(y_formatter) 
        ax.set_xlabel("Time (sec)")
        #The y label gets split into lines of 40 characters for readability 
        ax.set_ylabel("\n".join(wrap(y_axis_label,40)))
        ax.set_title("Attempt {:03d}".format(i))
        #Get the length of a random list in the data (they should all be
        #the same length) and create the x axis tick labels based on this
        x_axis = create_x_axis_tick_labels(len(d.itervalues().next()))
        #Finally, draw the plot
        if is_port_data:
            #set y axis bounds and pad the top
            ax.set_ylim([0, max_y+(max_y*0.01)])
            ax.stackplot(x_axis, d.values(), labels=d.keys(), colors=COLOURS)
        else:
            j = 0 
            for key in d.iterkeys():
                x_axis = create_x_axis_tick_labels(len(d.get(key)))
                colour = COLOURS[j]
                if MASTER_HOSTNAME not in d:
                    colour = COLOURS[j+1]
                ax.plot(x_axis, d.get(key), label=key, color=colour)
                j += 1
        i += 1

    #The title gets split into lines of 80 characters for readability
    title = plt.suptitle("\n".join(wrap(graph_title,80)))
    legend = plt.legend(bbox_to_anchor=(0,-0.4),ncol=4,loc="lower center")
    #ensures that none of the subplots are overlapping
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(graph_filename, dpi=300, bbox_extra_artists=(title,legend,), bbox_inches='tight')

"""
Get subdirectories when given a path
"""
def get_subdirectories(path):
    subdirectories = []
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path, filename)):
            subdirectories.append(filename)
    return subdirectories

"""
Gets the max y value for port data. 
Converts the value to megabits if specified.
"""
def get_max_yaxis_port(filename, convert_to_bits):
    max_y = -1
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = float(row["derivative"])
            if convert_to_bits:
                value= (value*8)/1000000
            if max_y < value:
                max_y = value
    return max_y

"""
Get the max y value for non port data.
Returns the max y when the master node data 
is included and also when it is not included.
This is because the graphs get drawn twice:
once with the master node and once without it.
"""
def get_max_yaxis(filename):
    max_master = -1
    max_no_master = -1
    with open(filename) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            value = float(row["value"])
            node = row["tags"]
            if max_master < value:
                max_master = value
            if node != "elf-cluster" and max_no_master < value:
                max_no_master = value
    return (max_master, max_no_master)

def remove_inactive(stats):
    """
    Remove entries where the node/port is inactive.
    Being inactive means the values of the stats collected is 0.
    """
    for stat_name, stat_vals in stats.items():
        inactive = True
        for val in stat_vals:
            if val > 0:
                inactive = False
                break
        if inactive:
            del stats[stat_name]

"""
Generate graphs using the data from the subdirectories of the given one
"""
def generate_graph(directory, graph_title):
    directories = sorted(get_subdirectories(directory))
    network_data_to_process = [
                    #port stats
                    ("bytes_in", "Mbps transmitted by nodes", True, True),
                    ("bytes_out", "Mbps received by nodes", True, True),
                    ("packets_in", "pps transmitted by nodes", True, False),
                    ("packets_out", "pps received by nodes", True, False),
                    #non-port stats
                    ("cpu_percent","CPU utilisation (%)", False, False),
                    ("disk_usage","Percentage of disk space used", False, False),
                    ("virtual_memory","Percentage of memory used", False, False)
                    ]
    
    for measurement, y_axis_label, is_port_data, convert_to_bits in network_data_to_process:
        data = []
        #find the maximum y-value so that the y-axis scale is the same for all graphs
        max_num = - 1
        #for non-port stats, it also draws a graph without the master node, so need the max y value without the master
        max_num_no_master = -1

        for dir_path in directories:
            #read in the csv file into an ordered dict
            info = read_csv(os.path.join(directory,dir_path, "indv_ports_"+ measurement + ".csv"),is_port_data, convert_to_bits)
            remove_inactive(info)
            data.append(info)

            #get the max y-value for this directory
            if is_port_data: 
                #need to pass in the all_ports data because the indv_port data is stacked on top of each other, so the max indv_port data is too low 
                dir_max = get_max_yaxis_port(os.path.join(directory,dir_path,"all_ports_"+ measurement + ".csv"), convert_to_bits)
            else:
                max = get_max_yaxis(os.path.join(directory,dir_path,"indv_ports_"+ measurement + ".csv"))
                dir_max = max[0]
                if max[1] > max_num_no_master:
                    max_num_no_master = max[1]
            
            if dir_max > max_num:
                max_num = dir_max

        plot_all(data, graph_title, y_axis_label, os.path.join(directory, measurement + ".png"), is_port_data, max_num)

        #re-graph without the master if it is non-port stats
        if not is_port_data:
            for d in data:
                del d["elf-cluster"]
            plot_all(data, graph_title + " without master", y_axis_label, os.path.join(directory, measurement + "_no_master.png"), is_port_data, max_num_no_master)

if __name__ == "__main__":
    generate_graph(sys.argv[1], sys.argv[2])
