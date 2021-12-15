import pandas as pd
import os
import matplotlib.pyplot as plt
from matplotlib import cycler
import numpy as np

# Styling based on https://jakevdp.github.io/PythonDataScienceHandbook/04.11-settings-and-stylesheets.html
colors = cycler('color',
                ['#EE6666', '#3388BB', '#9988DD',
                 '#EECC55', '#88BB44', '#FFBBBB'])
plt.rc('axes', facecolor='#E6E6E6', edgecolor='none',
       axisbelow=True, grid=True, prop_cycle=colors)
plt.rc('grid', color='w', linestyle='solid')
plt.rc('xtick', direction='out', color='gray')
plt.rc('ytick', direction='out', color='gray')
plt.rc('patch', edgecolor='#E6E6E6')
plt.rc('lines', linewidth=2)

def main():
  threads, rawEvents, BPFContainEventsSent, BPFCAuditEventsCaptured = getPerfStats('OldMethod')
  
  # Backend Graphs
  # Events sent by BPFContain vs. raw events produced
  # Data
  x_axis = np.arange(len(threads))
  rawEvents = list(np.array(rawEvents) / 10 ** 6)
  BPFContainEventsSentInMillions = np.array(BPFContainEventsSent) / 10 ** 6
  
  # Plots
  _, ax = plt.subplots()
  ax.bar(x_axis - 0.2, rawEvents, width=0.4, label = "Produced")
  ax.bar(x_axis + 0.2, BPFContainEventsSentInMillions, width=0.4, label = "Published")
  ax.axhline(y=np.mean(BPFContainEventsSentInMillions), color='black', label="Published x̄")

  # Legend
  ax.legend()
  ax.set_title('Number of Events Produced vs. Published by BPFContain')
  ax.set_xlabel('Number of Event Producer Threads')
  ax.set_ylabel('Number of Events (in millions)')

  # Change ordering of legend https://stackoverflow.com/a/46160465
  handles, labels = plt.gca().get_legend_handles_labels()
  order = [1,2,0]
  plt.legend([handles[idx] for idx in order],[labels[idx] for idx in order])

  plt.xticks(x_axis, threads)
  plt.savefig("../figures/Events_Produced_vs_Published")
  
  plt.clf()

  # Events sent by BPFContain vs. ingested by BPFCAudit 
  _, ax = plt.subplots()
  ax.bar(x_axis - 0.2, BPFContainEventsSent, width=0.4, label = "Published")
  ax.bar(x_axis + 0.2, BPFCAuditEventsCaptured, width=0.4, label = "Ingested")

  # Legend
  ax.legend()
  ax.set_title('Number of Events Published by BPFContain vs. Ingested by BPFCAudit')
  ax.set_xlabel('Number of Event Producer Threads')
  ax.set_ylabel('Number of Events (in millions)')

  plt.xticks(x_axis, threads)
  plt.savefig("../figures/Events_Produced_vs_Ingested_Old_Method")

  plt.clf()

  # Frontend Graphs

  # Audit Modal Render Time
  numberOfAudits, avgRenderTime = getAuditModalStats()
  x_axis = np.array(numberOfAudits)
  m, b = np.polyfit(numberOfAudits, avgRenderTime, 1)
  
  # Plots
  _, ax = plt.subplots()
  ax.plot(x_axis, avgRenderTime, 'o')
  ax.plot(x_axis, m*x_axis + b)

  # Labels
  ax.set_title('Average Render Time of Audit Modal With Varying Amounts of Audits')
  ax.set_xlabel('Number of Audits')
  ax.set_ylabel('Average Render Time (ms)')

  plt.xticks(x_axis, numberOfAudits)
  plt.savefig("../figures/Audit_Modal_Render_Time")

  plt.clf()

  # Policy Heatmap Render Time
  numberOfLines, avgRenderTime = getPolicyHeatMapStats()
  x_axis = np.array(numberOfLines)
  m, b = np.polyfit(numberOfLines, avgRenderTime, 1)
  
  # Plots
  _, ax = plt.subplots()
  ax.plot(x_axis, avgRenderTime, 'o')
  ax.plot(x_axis, m*x_axis + b)
  ax.set_ylim([50, 250])

  # Labels
  ax.set_title('Average Render Time of Policy Heatmap With Varying Policy Sizes')
  ax.set_xlabel('Number of Lines in Policy')
  ax.set_ylabel('Average Render Time (ms)')

  plt.xticks(x_axis, numberOfLines)
  plt.savefig("../figures/Policy_Heatmap_Render_Time")

def getPerfStats(perf_filename: str):
  my_csv = pd.read_csv(os.path.join('Backend-Perf', perf_filename + '.csv'))

  return list(my_csv['Threads']), list(my_csv['Raw events']), list(my_csv['BPFContain Audit Events Captured']), list(my_csv['Audit Events Captured by Backend'])

def getAuditModalStats():
  my_csv = pd.read_csv(os.path.join('Frontend-Perf', 'AuditModalRenderTime.csv'))

  return list(my_csv['Number of audits'].astype(int)), list(my_csv['Average render time over 5 trials (ms)'])

def getPolicyHeatMapStats():
  my_csv = pd.read_csv(os.path.join('Frontend-Perf', 'PolicyHeatmapRenderTime.csv'))

  return list(my_csv['Number of lines in policy']), list(my_csv['Render time over 5 trials (ms)'])
      
main()