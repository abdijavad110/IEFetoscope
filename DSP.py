import time
import mpld3
import threading
import numpy as np
from mpld3 import plugins
from scipy.signal import *
import matplotlib.pyplot as plt
from scipy.stats import mode

from HTTP_handler import Server

SIGNAL_T = 5

last_time = time.time()


class Filters:
    FS = 1000
    LOWCUT = 25
    HIGHCUT = 250

    @staticmethod
    def butter_bandpass(lowcut, highcut, fs, order=6):
        nyq = 0.5 * fs
        low = lowcut / nyq
        high = highcut / nyq
        b, a = butter(order, [low, high], btype='band')
        return b, a

    @staticmethod
    def remove_outlier(data):
        avg = data.sum() / len(data)
        f1 = avg - 1000 < data
        f2 = data < avg + 1000
        return data[f1 & f2]

    @staticmethod
    def butter_bandpass_filter(data, lowcut, highcut, fs, order=6):
        b, a = Filters.butter_bandpass(lowcut, highcut, fs, order=order)
        y = lfilter(b, a, data)
        return y

    @staticmethod
    def average(data, depth=1):
        out = np.zeros(len(data) - 2 * depth)
        for i in range(depth, len(data) - depth):
            out[i - depth] += [sum(data[i - depth:i + depth + 1]) / (2 * depth + 1)]
        return out

    @staticmethod
    def apply(data):
        ds = 10
        avg = 20

        # data = Filters.remove_outlier(data)

        data = Filters.butter_bandpass_filter(data, Filters.LOWCUT, Filters.HIGHCUT, Filters.FS, order=3)

        data = wiener(data, mysize=150)
        wienered = data

        data = np.abs(hilbert(data))
        down_data = decimate(Filters.average(data, avg), ds) * 2

        peaks, _ = find_peaks(down_data, distance=10, prominence=250, width=1)

        # fig, ax = plt.subplots(figsize=(12, 4.5))
        # l, = ax.plot(down_data)
        # ax.plot(peaks, down_data[peaks], 'r*')
        # handles, labels = ax.get_legend_handles_labels()  # return lines and labels
        # interactive_legend = plugins.InteractiveLegendPlugin(zip(handles,
        #                                                          ax.collections),
        #                                                      labels,
        #                                                      alpha_unsel=0.5,
        #                                                      alpha_over=1.5,
        #                                                      start_visible=True)
        # plugins.connect(fig, interactive_legend)
        #
        # html_fig = mpld3.fig_to_html(fig)

        return peaks
        # return peaks, html_fig


class Processor:
    def __init__(self):
        self.HRs = []
        self.peaks = []
        self.buffer = None
        self.received_idx = -1
        self.new_data_lock = threading.Lock()
        self.new_data_lock.acquire()
        threading.Thread(target=self._calculate_HR, daemon=True).start()
        threading.Thread(target=Server.initiate, daemon=True).start()

        self.hr_file = open("../results/hr_" + str(time.time()), 'w')

    def new_data(self, b):
        self.buffer = b
        self.received_idx += 1
        self.new_data_lock.release()

    def _calculate_HR(self):
        while True:
            self.new_data_lock.acquire()
            # extract signal
            self.signal = np.zeros(len(self.buffer) // 2, dtype=np.uint16)
            for i in range(len(self.buffer) // 2):
                self.signal[i] = int(self.buffer[2 * i + 1]) * 16 + int(self.buffer[2 * i])

            peaks = Filters.apply(self.signal) / (Filters.FS / 10) + self.received_idx * SIGNAL_T
            # peaks, html_fig = Filters.apply(self.signal)
            # hr = len(peaks) * 60 // SIGNAL_T
            delays = np.diff(peaks)
            delays = delays[np.bitwise_and(0.28 < delays, delays < 1)]
            print(" => mean: %d, median: %d, mode: %d       " % (int(60 / np.mean(delays)) if len(delays) > 0 else 0,
                  int(60 / np.median(delays)) if len(delays) > 0 else 0,
                  int(60 / mode(delays).mode[0]) if len(delays) > 0 else 0) + str(delays))
            last_hr = self.HRs[-1] if len(self.HRs) else 0
            hr = int(60 / np.median(delays)) if len(delays) > 0 else last_hr
            hr = hr if 70 < hr < 200 else last_hr
            # hr = len(peaks) * 60 // SIGNAL_T

            self.HRs.append(hr)
            self.hr_file.write("%d\n" % hr)
            self.hr_file.flush()
            self.peaks += peaks.tolist()

            Server.new_info(FHR.extract_data(self.HRs), self.draw_plot())

    def draw_plot(self):
        fig, ax = plt.subplots(figsize=(12, 4.5))

        # ax.hlines(170, 0, 1200, colors='#ffeaea', linewidths=75)
        # ax.hlines(100, 0, 1200, colors='#ffeaea', linewidths=75)

        T = np.linspace(0, self.received_idx * 5 / 60, self.received_idx + 1)
        l, = ax.plot(T, self.HRs, color='royalblue')
        ax.hlines(sum(self.HRs) // len(self.HRs), min(T), max(T), colors='teal')
        handles, labels = ax.get_legend_handles_labels()  # return lines and labels
        interactive_legend = plugins.InteractiveLegendPlugin(zip(handles,
                                                                 ax.collections),
                                                             labels,
                                                             alpha_unsel=0.5,
                                                             alpha_over=1.5,
                                                             start_visible=True)
        plugins.connect(fig, interactive_legend)
        ax.set_ylabel('Heart Rate')
        ax.set_xlabel('Time')
        ax.set_xlim(0, 20)
        ax.set_ylim(90, 180)

        ax.grid(True, alpha=0.3)

        return mpld3.fig_to_html(fig)


class FHR:
    @staticmethod
    def extract_data(hrs):
        hrs = np.array(hrs)
        # heart rate
        hr = hrs[-1]

        # baseline: majority, simple average, ...
        bl = sum(hrs) // len(hrs)

        # variation
        vr = "moderate"
        if len(hrs) >= 24:
            var_val = max(hrs[-24:]) - min(hrs[-24:])
            if var_val <= 5:
                vr = "minimal"
            elif var_val >= 25:
                vr = "marked"

        # acceleration
        ac = 0
        if len(hrs) >= 12:
            ac = FHR.find_acc(hrs, bl)

        return hr, bl, ac, vr

    @staticmethod
    def find_acc(hrs, bl):
        ac = 0
        last_end = 0
        for start in range(len(hrs) - 1):
            if start < last_end:
                continue
            if bl - 5 < hrs[start] < bl + 5:
                for end in range(start + 5, len(hrs)):
                    if bl - 5 < hrs[end] < bl + 5:
                        samples = hrs[start + 1:end]
                        peak_idx = np.argmax(samples)
                        if (samples <= bl).any():
                            break
                        if (peak_idx - start) > (30 // SIGNAL_T) or (end - start) > (120 // SIGNAL_T):
                            break
                        peak_end_dist = end - peak_idx

                        check_idx = (samples >= 15 + bl)[
                                    peak_idx - 3:peak_idx + (4 if peak_end_dist > 4 else peak_end_dist)]
                        if np.count_nonzero(check_idx) <= 3:
                            break
                        else:
                            print("Found an acceleration start: %d end: %d" % (start * SIGNAL_T, end * SIGNAL_T))
                            last_end = end
                            ac += 1
                            break
                    else:
                        continue
            else:
                continue

        return str(ac)
