import random
import math

ARRIVAL = 0
DEPARTURE = 1
OBSERVER = 2
DROPPED = 3

def GenerateX(lamb):
    return -1 / lamb * math.log(1-random.random())

def CalcMeanAndVariance(lamb):
    #Calculate mean and variance of GenerateX function
    variables = []
    for i in range(1000):
        variables.append(GenerateX(lamb))
    meanX = sum(variables)/1000
    res = sum((i - meanX) ** 2 for i in variables) / len(variables)
    print(res) # this is variance
    print(meanX)

def Sort_Tuple(tup):
 
    # reverse = None (Sorts in Ascending order)
    # key is set to sort using second element of
    # sublist lambda has been used
    tup.sort(key = lambda x: x[1])
    return tup

# Length of packets in bits
# C = The transmission rate of the output link in bits per second.
def GenerateServiceTime(L, C):
    # Service time is L / C
    return GenerateX(1/L) / C

def GenerateEventList(T, L, C, queue_max):
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
            next_departure_time = GenerateServiceTime(L, C) + last_departure_time
            departure_events.append([DEPARTURE, next_departure_time])
            time = next_departure_time
            num_pkts_in_queue -= 1
            while (True):
                if events[arrival_index][1] <= time: # this indexerrors sometimes
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

def CalculateMetrics(events):
    Na = Nd = No = Ndrop = num_pkts_in_queue = Tidle = last_departure_time = 0
    E = []
    for i, event in enumerate(events):
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



if __name__ == "__main__":
    lamb = 75 # lambda
    T = 1000
    L = 2000 # avg length of packets in bits
    C = 1e6
    queueSize = None # None is infinite queue
    events = GenerateEventList(T, L, C, queueSize)

    metrics = CalculateMetrics(events)
    print(metrics)
    
