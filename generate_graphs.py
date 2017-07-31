import matplotlib.pylab as plt
from matplotlib.ticker import ScalarFormatter
from collections import OrderedDict
import os
from textwrap import wrap
import sys


colours = ["#e6194b","#3cb44b","#ffe119", "#f58231", "#911eb4", "#46f0f0", "#000080", "#aa6e28", "#800000", "#808080", "#fabebe"]
"""
Read in the csv. Each row is appended to a list.
Measurements for ports 12-26 are discarded since these
ports are not used. 
"""
def read_csv(filename, is_port_data):
    csv_rows = []
    with open(filename) as f:
        next(f) #skip the header line
        for line in f:
            row = line.split(',')
            #if this is port data, filter some ports
            if is_port_data:
                port_name = row[1]
                #get the port number from the port name
                port_num = int(port_name[4:]) 
                #only deal with ports 1-11 since the other ports are unused
                if port_num > 11:
                    continue

            #delete first element since it just states the type of 
            #measurement (i.e bytes_in)
            del row[0]
            csv_rows.append(row)
    return csv_rows

"""
Create an ordered dict with an entry for each port.
Each value contains a list of measurements associated 
with that port. The convert_to_bits param is an option
on whether the measurement should be converted to 
megabits per second. 
"""
def split_ports(csv_rows,convert_to_bits=False):
    port_info = OrderedDict()
    current_port = None

    for i in range(0,len(csv_rows)):
        row = csv_rows[i]
        value = float(row[2])
        if convert_to_bits:
            value = (value*8)/1000000 #byte/sec to megabit/sec
        
        if current_port != row[0]:
            #new port, so create an empty list to store measurements on
            current_port = row[0]
            value_list =[]
            port_info[current_port] = value_list

        port_info.get(current_port).append(value)

    return port_info

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

def get_colour(index, key, length):
    print "key: {} index: {} length: {}".format(key,index, length)
    if length == len(colours):
        if index == 0:
            return colours[2]
        elif index <= 2:
            return colours[(index-1)]
        else: 
            return colours[index]
    
    if index > 1:
            return colours[index + 1]
    return colours[index]

"""
Create a graph from the data given. Each element in the data represents 
a subplot in the graph. The graph will be titled with the param: graph_title
and label the y axis with the param: y axis label. Finally, it will be saved
as a png file named with the param: graph_filename.
"""
def plot_all(data, graph_title, y_axis_label, graph_filename, is_port_data):

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
        # x_axis = create_x_axis_tick_labels(len(d.itervalues().next()))
        #Finally, draw the plot
        if is_port_data:
            ax.stackplot(x_axis,d.values(),labels=d.keys(),colors=colours)
        else:
            j = 0 
            for key in d.iterkeys():
                x_axis = create_x_axis_tick_labels(len(d.get(key)))
                colour = get_colour(j,key, len(d))
                ax.plot(x_axis,d.get(key),label=key, color= colour)
                j += 1
        i += 1

    #The title gets split into lines of 80 characters for readability
    title = plt.suptitle("\n".join(wrap(graph_title,80)))
    legend = plt.legend(bbox_to_anchor=(0,-0.4),ncol=4,loc="lower center")
    #ensures that none of the subplots are overlapping
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig.savefig(graph_filename, dpi=300, bbox_extra_artists=(title,legend,), bbox_inches='tight')

def get_subdirectories(path):
    subdirectories = []
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path, filename)):
            subdirectories.append(filename)
    return subdirectories

"""
Generate graphs using the data from the subdirectories of the given one
"""
def generate_graph(directory, graph_title):
    directories = sorted(get_subdirectories(directory))
    network_data_to_process = [
                    ("bytes_in", "Mbps transmitted by nodes", True, True),
                    ("bytes_out", "Mbps received by nodes", True, True),
                    ("packets_in", "pps transmitted by nodes", True, False),
                    ("packets_out", "pps received by nodes", True, False),
                    ("cpu_percent","CPU utilisation (%)", False, False),
                    ("disk_usage","Percentage of disk space used", False, False),
                    ("virtual_memory","Percentage of memory used", False, False)
                    ]
    
    for measurement, y_axis_label, is_port_data, convert_to_bits in network_data_to_process:
        data = []
        for dir_path in directories:
            #read in the csv file into a list
            csv_rows = read_csv(os.path.join(directory,dir_path, "indv_ports_"+ measurement + ".csv"),is_port_data)
            info = split_ports(csv_rows, convert_to_bits)
            data.append(info)

        plot_all(data, graph_title, y_axis_label, os.path.join(directory, measurement + ".png"), is_port_data)

        if not is_port_data:
            for d in data:
                del d["elf-cluster"]
            plot_all(data, graph_title + " without master", y_axis_label, os.path.join(directory, measurement + "_no_master.png"), is_port_data)

if __name__ == "__main__":
    generate_graph(sys.argv[1], sys.argv[2])
