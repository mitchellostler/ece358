import random
import math
import matplotlib.pyplot as plt

ARRIVAL = 0
DEPARTURE = 1
OBSERVER = 2
DROPPED = 3

def event_p(events):
    for e in events:
        if e[0] == 0:
            strt = "ARRIVAL"
        if e[0] == 1:
            strt = "DEPARTURE"
        if e[0] == 2:
            strt = "OBSERVER"
        if e[0] == 3:
            strt = "DROPPED"
        print(strt, e[1], "\n") 

# Generate exponential random variable x based on lamba value
def GenerateX(lamb):
    return -1 / lamb * math.log(1-random.random())

# sort events based on second element. The second element is time stamp of event
# sorts in ascending order
def Sort_Tuple(events):
    events.sort(key = lambda x: x[1])
    return events

# Length of packets in bits
# C = The transmission rate of the output link in bits per second.
def GenerateServiceTime(L, C):
    # Service time is L / C
    return GenerateX(1/L) / C

def GenerateEventList(T, L, C, queue_max, lamb):
    events = []
    # Generate Arrival Events
    time = 0
    while(time < T):
        time = time + GenerateX(lamb)
        events.append([ARRIVAL, time]) 
    # Generate Departures
    time = 0
    num_pkts_in_queue = 0
    arrival_index = 0
    last_departure_time = 0
    departure_events = []
    while(time < T):
        if num_pkts_in_queue == 0:
            time = events[arrival_index][1]
            last_departure_time = time
            arrival_index += 1
            num_pkts_in_queue += 1
        elif num_pkts_in_queue > 0:
            # Calculate departure times, catching up to current time
            next_departure_time = last_departure_time = GenerateServiceTime(L, C) + last_departure_time
            departure_events.append([DEPARTURE, next_departure_time])
            time = next_departure_time
            num_pkts_in_queue -= 1
            while (True):
                if len(events) <= arrival_index:
                    break
                if events[arrival_index][1] <= time:
                    if not queue_max or num_pkts_in_queue < queue_max:
                        num_pkts_in_queue += 1
                    else:
                        events[arrival_index][0] = DROPPED

                    arrival_index += 1
                else:
                    break
    events += departure_events

    # Generate observer events
    time = 0
    while(time < T):
        time = time + GenerateX(5*lamb)
        events.append([OBSERVER, time]) 

    # Sort events
    Sort_Tuple(events)
    return events

def CalculateMetrics(events, T):
    Na = Nd = No = Ndrop = num_pkts_in_queue = Tidle = last_departure_time = 0
    E = []
    for event in events:
        if event[0] == ARRIVAL:
            Na += 1
            num_pkts_in_queue += 1
        elif event[0] == DEPARTURE:
            Nd += 1
            num_pkts_in_queue -=1
            last_departure_time = event[1]
        elif event[0] == DROPPED:
            Ndrop += 1
        elif event[0] == OBSERVER:
            No += 1
            # Record time-average of number of packets in queue E[N]
            E.append(num_pkts_in_queue)
            # Sum up idle time
            if num_pkts_in_queue == 0:
                Tidle += event[1] - last_departure_time
                last_departure_time = event[1]

    Pidle = Tidle / T
    Ploss = Ndrop / Na
    Eavg = sum(E) / len(E)

    return {"Pidle": Pidle, "Ploss": Ploss, "Eavg": Eavg}

def q1(lamb):
    print("Q1: ")
    #Calculate mean and variance of GenerateX function
    variables = []
    for i in range(1000):
        variables.append(GenerateX(lamb))
    meanX = sum(variables)/1000
    res = sum((i - meanX) ** 2 for i in variables) / len(variables)
    print("Variance: " + str(res)) # this is variance
    print("Mean: " + str(meanX))

def q3():
    print("Q3: ")
    T = 5 #1000
    L = 2000 # avg length of packets in bits
    C = 1e6
    queueSize = None # None is infinite queue
    # Generate rho values between 0.25 and 0.95 with step size of 0.1
    rho_values = []
    r = 0.25
    while(r <= 0.95):
        rho_values.append(r)
        r += 0.1

    eavg_vals = []
    pidle = []
    for r in rho_values:
        lamb = r*C/L
        evs = GenerateEventList(T, L, C, queueSize, lamb)
        eavg_vals.append(CalculateMetrics(evs, T)["Eavg"])
        pidle.append(CalculateMetrics(evs, T)["Pidle"])
        print(f"Rho: {round(r, 2)}, E[N]: {round(eavg_vals[-1], 2)} "
                f"Ploss: {round(pidle[-1], 2)}")
    
    # plt.plot(rho_values, eavg_vals)
    # plt.xlabel('Rho')
    # plt.ylabel('Pidle')
    # plt.show()

def q4():
    print("Q4: ")
    T = 5 #1000
    L = 2000 # avg length of packets in bits
    C = 1e6
    queueSize = None # None is infinite queue
    r = 1.2
    lamb = r*C/L
    evs = GenerateEventList(T, L, C, queueSize, lamb)
    print(CalculateMetrics(evs, T))

def q6():
    print("Q6:")
    T = 5 #1000
    L = 2000 # avg length of packets in bits
    C = 1e6
    Ks = [10, 25, 50]
    for  k in Ks:
        # Generate rho values between 0.25 and 0.95 with step size of 0.1
        rho_values = []
        r = 0.5
        while(round(r, 2) <= 1.5):
            rho_values.append(r)
            r += 0.1
        eavg_vals = []
        ploss_vals = []
        print(f"K = {k}")
        for r in rho_values:
            lamb = r*C/L
            evs = GenerateEventList(T, L, C, k, lamb)
            mets = CalculateMetrics(evs, T)
            eavg_vals.append(mets["Eavg"])
            ploss_vals.append(mets["Ploss"])
            print(f"Rho: {round(r, 2)}, E[N]: {round(eavg_vals[-1], 2)} "
                f"Ploss: {round(ploss_vals[-1], 2)}")
        # plt.plot(rho_values, eavg_vals, label=f"K={k}")
        # plt.xlabel('Rho')
        # plt.ylabel('P_loss')
        
    # plt.title('P_loss vs Rho values')
    # plt.legend(loc='upper left')
    # plt.show()


if __name__ == "__main__":
    q1(75)
    q3()
    q4()
    q6()
    
