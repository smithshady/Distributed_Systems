import math
import matplotlib.pyplot as plt

# Read results from file
with open('../files/results.txt') as f:
    lines = f.readlines()
lines = [l.strip().split(',') for l in lines]

num_messages = []
n_arr = []
edges = []
com_cost_arr = []
times = []

# Parse the data from each line
for line in lines:
    n = int(line[2])
    n_edges = int(line[3])
    num_messages.append(int(line[1]))
    n_arr.append(n)
    edges.append(n_edges)
    com_cost_arr.append(2*n_edges + 5*n*math.log(n))
    times.append(float(line[4]))  # Assuming timing data is in column 4

# Create a 2x2 subplot
fig, axs = plt.subplots(2, 3, figsize=(14, 8))

# Plot n_arr vs #Messages
axs[0, 0].plot(n_arr, num_messages, 'bs-')
axs[0, 0].set_title('Nodes vs #Messages')
axs[0, 0].set_xlabel('Nodes')
axs[0, 0].set_ylabel('#Messages')

# Plot Edges vs #Messages
axs[0, 1].plot(edges, num_messages, 'g^-')
axs[0, 1].set_title('Edges vs #Messages')
axs[0, 1].set_xlabel('Edges')
axs[0, 1].set_ylabel('#Messages')

# Plot 2E + 5NlogN vs #Messages
axs[0, 2].plot(com_cost_arr, num_messages, 'g^-')
axs[0, 2].set_title('Communication cost vs #Messages')
axs[0, 2].set_xlabel('2E + 5NlogN')
axs[0, 2].set_ylabel('#Messages')

# Plot n_arr vs Time
axs[1, 0].plot(n_arr, times, 'rs-')
axs[1, 0].set_title('Nodes vs Time')
axs[1, 0].set_xlabel('Nodes')
axs[1, 0].set_ylabel('Time (s)')

# Plot Edges vs Time
axs[1, 1].plot(edges, times, 'k^-')
axs[1, 1].set_title('Edges vs Time')
axs[1, 1].set_xlabel('Edges')
axs[1, 1].set_ylabel('Time (s)')

# Adjust layout to prevent overlap
plt.tight_layout()

# Show the plots
plt.show()
