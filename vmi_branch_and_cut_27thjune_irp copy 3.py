
import numpy as np                                                          #to process numbers and generate random numbers
filename=input('Enter the data file name: ')
df= open(filename)                                                      #
data = df.readlines()                                                      #df to read lines in the file
n = int(data[0].split()[0])-1                                               #number of customers
Q = int(data[0].split()[2])                                                 #max capacity of the vihicle used, Q
H = int(data[0].split()[1])                                                 #Time horizon, H
SSI = int(data[1].split()[3])                                                #starting inventory at supplier considered infinite or large number
K = float('inf')
print("SSI, starting supplier inventory: "+str(SSI))
N = [i for i in range(1, n+1)]                                              #N list of customer numbers
print("List of customers: "+str(N))                                         #(1)N is customer list from 1 to n because python starts a set of numbers from zero as index
P = [0] + N                                                                 #total number of points to be plotted includes depot
print("List of supplier+customers: "+str(P))                                #(1)n is customer list from 1 to n because python starts a set of numbers from zero as index
period=H
print("period, H/T: "+str(H))
demand={}                                                                   # demand dictionary of demand for respective cust.
I_end={}                                                                    # I, max inventory dictionary of demand for respective cust.       
h={}                                                                        # holding cost dictionary respective cust.
SRI={}                                                                  # SRI starting inventory dictionary respective cust.
U_max={}                                                                        # max inventory dictionary respective cust.
prev_end_inv={}
j=2                                                                         #                                                         
for i in N:                                                                 # input for all variables
    demand[i] = int(data[j].split()[6])                                     #is this changing?
    U_max[i] = int(data[j].split()[4])                  
    h[i] = float(data[j].split()[7])    
    SRI[i] = int(data[j].split()[4])
    j+=1      
I_end = prev_end_inv=U_max    
print("retailer demand: "+str(demand))                                                               #(3)#prints all customers with demand in dictionary format
print("Ending_retailer_inventory: "+str(I_end))
print("retailer_inventoryholding_cost: "+str(h))
print("starting_retailer_inventory: "+str(SRI))
print("Max_retailer_inventory: "+str(U_max))
loc_x=[]                                                                      #loc_x emply list
loc_y=[]                                                                      #loc_x emply list
for i in range(1,len(P)+1):
    loc_x.append(float(data[i].split()[1]))                                       #to input x coordinates of node
    loc_y.append(float(data[i].split()[2]))                                       #to input y coordinates of node
print("x coordinates: "+str(loc_x))
print("y coordinates: "+str(loc_y))
import matplotlib.pyplot as plt                                                   #import library to plot and graph
from docplex.mp.model import Model                                            #imports cplex to do optimizations with cplex functions
plt.scatter(loc_x[1:], loc_y[1:], c='g')                                      #graph features from location 1 to last location, that is all customers.
for i in N:                                                                   #characteristics of customer locations on chart
    plt.annotate('$demand_%d=%d$' % (i, demand[i]), (loc_x[i]+2, loc_y[i]))   #plots demand string on graph for each customer
plt.plot(loc_x[0], loc_y[0], c='b', marker='*')                               #characteristics of depot node with colour blue, and a square shape
plt.axis('scaled')                                                            #scales graph
plt.show()                                                                   #shows graph
plt.clf()                                                            
mdl = Model('IRP FOR VMI')                                                   #mdl creates a model and #prints the name before solution starts
E = [(i, j) for i in P for j in P if i != j]                                  #E is a list of combinations of (possible)travel edges where i is not equal to j

print("Edges: "+str(E))                                                                      #(4) #prints edge combination list
c = {(i, j): np.hypot(loc_x[i]-loc_x[j], loc_y[i]-loc_y[j]) for i, j in E}    #euclidean distance between nodes itself is cost
print("Euc. dist. between nodes: "+str(c))                                                                      #(5) #prints cost list
u = mdl.continuous_var_dict(N, ub=Q, name='u')                                #ub upperbound limits to total capacity of vehicle, continuous variable dictionary used because there are 10 customers, the other choice of dict var is binary
print(u)
for T in range(period):                                       #not right
    x = mdl.binary_var_dict(E, name='x'+str(T))                                          #xij is a dictionary of binary variables 0 or 1, where i, and j belong to arcs not nodes
    #print(x)
    print("starting retailer inventory: "+str(SRI))
    print("previous end inventory: "+str(prev_end_inv))
    print("ending inventory: "+str(I_end))                                                        
    cur_end_const=[0]                                                                    #I constant, a list of inventory 
    D_const=[0]
    U_const=[0]
    v_const = [0]
    delivery = [0]*(n+1)
    z=[0]*(n+1)
    y={a:0 for a in E}
    cnt=0
    customer=-1
    '''for i in N:
        if SRI[i]<=demand[i]:                                         #this gives the value of z constraint for customers
            delivery[i]=U_max[i]-SRI[i] 
            z[i]=1   
            cnt+=1
            if cnt==1:
                customer=i
            else:
                y[i]=1
                customer=-1
        else:
            delivery[i]=0
            z[i] = 0
         
    if cnt==1 and customer!=-1:
        y[customer] = 2'''
    prev=0
    active_arcs=[]
    for i in N:
        if SRI[i]<=demand[i]:        #checking inventory and demand to send the vehicle                                 #this gives the value of z constraint for customers
            active_arcs.append((prev,i))    
            delivery[i]=U_max[i]-SRI[i] 
            z[i]=1   
            cnt+=1
            prev=i
        else:
            delivery[i]=0
            z[i] = 0
    active_arcs.append((prev,0))
    if len(active_arcs)==1:
        y[active_arcs[0]]=2
    else:
        for a in active_arcs:
            y[a]=1
    #print(y)
    Del_const=[0]
    z_const,y_const=[0],[]
    for i in N:
        cur_end_const.append(mdl.continuous_var(I_end[i]))        #appending i_end as continuous variable
        v_const.append(mdl.continuous_var(SRI[i]==demand[i]))     #appending v constraint, i.e 
        D_const.append(mdl.continuous_var(demand[i]))             #appending D, demand
        U_const.append(mdl.continuous_var(U_max[i]))
        Del_const.append(mdl.continuous_var(delivery[i]))
        z_const.append(mdl.continuous_var(z[i]))
    for i in E:
        y_const.append(mdl.continuous_var(y[i]))
        
    distance=sum(c[i, j]*y[(i,j)] for i, j in E) #distance travelled on each day
    if distance!=0:
        distance+=sum(h[i]*I_end[i] for i in N) #calculating the cost based on distande

    mdl.add_constraints(mdl.sum(x[i, j] for j in P if j != i) == 1 for i in N)    #constraint: we consider c as the cost itself, hence here x assumed as 1 when it travels between two different nodes. 
    mdl.add_constraints(mdl.sum(x[i, j] for i in P if i != j) == 1 for j in N)    #constraint: we consider c as cost and x equals 1, for i in all points, i!=j, j is a custoner
    mdl.add_indicator_constraints(mdl.indicator_constraint(x[i, j], u[i]+demand[j] == u[j]) for i, j in E if i != 0 and j != 0) #constraint: this is used when a condition is to be met
    mdl.add_constraints(u[i] <= demand[i] for i in N)                      #(1e) constraint that says ui belongs to N of which depot is not a part
    mdl.set_objective("min",distance)                                      #setting objective based on distance and cost
    mdl.add_constraints(Del_const[i] == U_max[i]-SRI[i] for i in N)
    mdl.add_constraints(cur_end_const[i] >= prev_end_inv[i]-demand[i]+delivery[i] for i in N) #(1b) end_cur == prev_end - cur_demand + cur_delivery[i]
    mdl.add_constraints(cur_end_const[i] >=0 for i in N)                           #(1c)
    mdl.add_constraints(v_const[i] == True for i in N)
    mdl.add_constraints(demand[i] == U_const[i]-prev_end_inv[i] for i in N)                   #(1d) cur_demand<= u_max-i_prev
    mdl.add_constraints(D_const[i] <= Q for i in N)                                    #1f
    mdl.add_constraints(D_const[i] >= 0 for i in N)                                  #1k
    mdl.add_constraints(z_const[i] >= 1 for i in N)                                  #1g
    mdl.add_constraints(y_const[i] == 2 for i in range(len(E)))                                #1h
    
    solution = mdl.solve(log_output=True)  
    if solution!=None:                                       
        print(solution)
        solution.solve_status
    else:
        print("solution found")
        print("Objective:"+str(distance)) #when all the customers visited the cplex assumes it as optimal solution is achieved and gives none result, nothing to solve

    #print(active_arcs)
    plt.scatter(loc_x[1:], loc_y[1:], c='g')
    for i in N:
        plt.annotate('$demand_%d=%d$' % (i, demand[i]), (loc_x[i]+2, loc_y[i]))
    for i, j in active_arcs:
        plt.plot([loc_x[i], loc_x[j]], [loc_y[i], loc_y[j]], c='b', alpha=0.3)   #characteristics of arcs from customer i to customer j
    plt.plot(loc_x[0], loc_y[0], c='b', marker='*')                              #characteristics of depot node
    plt.axis('scaled')                                                        #to keep axes length equal
    plt.show()
    plt.clf()
    plt.close()
    mdl.print_information()
    prev_end_inv=I_end
    #prev_end_inv=SRI
    for i in N:
        if SRI[i]<=demand[i]:
            
            SRI[i]=U_max[i]
        else:
            
            SRI[i]-=demand[i]
    I_end = SRI
    #print(I_end)
   