import numpy as np                                                          #to process numbers and generate random numbers
df= open("abs5n10H3.dat")                                                      #enter file name and add file to the python path
data =  df.readlines()                                                      #df to read lines in the file
n = int(data[0].split()[0])-1                                               #number of customers
Q = int(data[0].split()[2])                                                 #max capacity of the vihicle used, Q
H = int(data[0].split()[1])                                                 #Time horizon, H
B = int(data[1].split()[3])                                                 #starting inventory at supplier considered infinite or large number
N = [i for i in range(1, n+1)]                                              #range function takes only till previous number, so (n+1) used
print("List of customers: "+str(N))                                         #(1)N is customer list from 1 to 10 because python starts a set of numbers from zero as index
P = [0] + N                                                                 #total number of points to be plotted
print("List of supplier+customers: "+str(P))                                                                    #(1)n is customer list from 1 to 10 because python starts a set of numbers from zero as index
demand={} 
U={}
h={}
I_start={}
j=2                                                                           #creates empty dictionary
for i in N:                                                                   #loop to create input for demands
    demand[i] = int(data[j].split()[6]) 
    U[i] = int(data[j].split()[4])
    h[i] = float(data[j].split()[7])    
    I_start[i] = int(data[j].split()[3])
    j+=1                                                                       
print("retailer and demand: "+str(demand))                                                               #(3)prints all customers with demand in dictionary format
print("Maximum_retailer_inventory: "+str(U))
print("retailer_inventoryholding_cost: "+str(h))
print("retailer_inventory_start: "+str(I_start))

loc_x=[]                                                                      #create loc_x empty list to append values
loc_y=[]                                                                      #create loc_y empty list to append values
for i in range(1,len(P)+1):
    loc_x.append(float(data[i].split()[1]))                                       #to input x coordinates of node
    loc_y.append(float(data[i].split()[2]))                                       #to input y coordinates of node
print("x coordinates: "+str(loc_x))
print("y coordinates: "+str(loc_y))
import matplotlib.pyplot as plt                                               #import library to plot and graph
plt.scatter(loc_x[1:], loc_y[1:], c='g')                                      #graph features from location 1 to last location, that is all customers.
for i in N:                                                                   #characteristics of customer locations on chart
    plt.annotate('$demand_%d=%d$' % (i, demand[i]), (loc_x[i]+2, loc_y[i]))   #plots demand string on graph for each customer
plt.plot(loc_x[0], loc_y[0], c='b', marker='*')                               #characteristics of depot node with colour blue, and a square shape
plt.axis('scaled')                                                            #scales graph
plt.show()                                                                    #shows graph
E = [(i, j) for i in P for j in P if i != j]                                  #E is a list of combinations of (possible)travel edges where i is not equal to j
print("Edges: "+str(E))                                                                      #(4) prints edge combination list
c = {(i, j): np.hypot(loc_x[i]-loc_x[j], loc_y[i]-loc_y[j]) for i, j in E}    #euclidean distance between nodes itself is cost
print("Euc. dist. between nodes: "+str(c))                                                                      #(5) prints cost list
from docplex.mp.model import Model                                            #imports cplex to do optimizations with cplex functions
import docplex.mp.solution as solution 
mdl = Model('CVRP FOR RMI')                                                   #mdl creates a model and prints the name before solution starts
x = mdl.binary_var_dict(E, name='x')                                          #xij is a dictionary of binary variables 0 or 1, where i, and j belong to arcs not nodes
print(x)
u = mdl.continuous_var_dict(N, ub=Q, name='u')                                #ub upperbound limits to total capacity of vehicle, continuous variable dictionary used because there are 10 customers, the other choice of dict var is binary
print(u)
mdl.minimize(mdl.sum(c[i, j]*x[i, j] for i, j in E))                          #objective is to min cij*xij where ij belong to arcs A
mdl.add_constraints(mdl.sum(x[i, j] for j in P if j != i) == 1 for i in N)    #constraint: we consider c as the cost itself, hence here x assumed as 1 when it travels between two different nodes. 
mdl.add_constraints(mdl.sum(x[i, j] for i in P if i != j) == 1 for j in N)    #constraint: we consider c as cost and x equals 1, for i in all points, i!=j, j is a custoner
mdl.add_indicator_constraints(mdl.indicator_constraint(x[i, j], u[i]+demand[j] == u[j]) for i, j in E if i != 0 and j != 0) #constraint: this is used when a condition is to be met
mdl.add_constraints(u[i] >= demand[i] for i in N)                             #constraint that says ui belongs to N of which depot is not a part
solution = mdl.solve(log_output=True)                                         
print(solution)
solution.solve_status
active_arcs = [a for a in E if x[a].solution_value > 0.9]                    #active arcs
plt.scatter(loc_x[1:], loc_y[1:], c='g')
for i in N:
    plt.annotate('$demand_%d=%d$' % (i, demand[i]), (loc_x[i]+2, loc_y[i]))
for i, j in active_arcs:
    plt.plot([loc_x[i], loc_x[j]], [loc_y[i], loc_y[j]], c='b', alpha=0.3)   #characteristics of arcs from customer i to customer j
plt.plot(loc_x[0], loc_y[0], c='b', marker='*')                              #characteristics of depot node
plt.axis('scaled')                                                            #to keep axes length equal
plt.show()                                                                   #showing plot