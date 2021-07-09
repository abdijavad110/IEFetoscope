import time
import numpy as np
import sounddevice as sd
from threading import Thread
from scipy.io import wavfile as wav
from matplotlib import pyplot as plt
from random import normalvariate as nrd
from random import randint as rd

HR = 60
RUN = False


class Tone:
    FREQ = 150
    Duration = 0.06
    SAMPLE_RATE = 10000

    sample_no = int(SAMPLE_RATE * Duration)
    tone = np.sin(np.linspace(0, 2 * np.pi * FREQ * Duration, sample_no))
    snr = 10
    fader = np.append(np.append(np.linspace(0, snr, 300), np.ones(sample_no - 600) * snr), np.linspace(snr, 0, 300))
    tone = tone * fader


def online_generator():
    while RUN:
        sd.play(Tone.tone, Tone.SAMPLE_RATE)
        delay = 60 / HR
        time.sleep(delay)


def offline_generator():
    dv = 0
    hrs = sig1 = [int(nrd(120, dv)) for _ in range(12 * 5)] + \
                 [120, 130, 140, 145, 150] + [int(nrd(150, dv)) for _ in range(12)] + [150, 140, 135, 130, 125, 120,
                                                                                       120] + \
                 [int(nrd(125, dv)) for _ in range(12 * 3)] + \
                 [int(nrd(120, dv)) for _ in range(12 * 1)] + [int(nrd(125, dv)) for _ in range(12 * 2)] + \
                 [130, 130, 130, 140, 142, 143] + [int(nrd(145, dv)) for _ in range(12)] + [140, 135, 130, 120, 110,
                                                                                            115] + \
                 [int(nrd(125, dv)) for _ in range(12 * 1)] + [int(nrd(120, dv)) for _ in range(12 * 2)] + \
                 [int(nrd(115, dv)) for _ in range(12 * 2)]
    hrs = sig2 = [int(nrd(120, dv)) for _ in range(12 * 2)] + \
          [int(nrd(115, dv)) for _ in range(12 * 2)] + \
          [int(nrd(110, dv)) for _ in range(12 * 2)] + \
          [110, 120, 130, 140, 150, 155, 150, 140, 130, 125, 120, 120] + \
          [int(nrd(120, dv)) for _ in range(12 * 1)] + \
          [int(nrd(110, dv)) for _ in range(12 * 3)] + \
          np.arange(119, 131).tolist() + [int(nrd(130, dv)) for _ in range(12 * 2)] + \
          [130, 130, 130, 140, 150, 155] + [int(nrd(155, dv)) for _ in range(12)] + [140, 130, 120, 110, 110, 110] + \
          [int(nrd(110, dv)) for _ in range(12 * 1)] + [int(nrd(115, dv)) for _ in range(12 * 1)] + \
          [int(nrd(110, dv)) for _ in range(12 * 1)] + [int(nrd(120, dv)) for _ in range(12 * 1)] + \
          [int(nrd(115, dv)) for _ in range(12 * 1)]
    hrs = sig3 = np.arange(110, 160, 1).tolist() + np.arange(160, 110, -1).tolist() + \
        np.array([110, 160, 120, 150, 130, 140]).repeat(6).tolist() + \
        np.array([110, 160, 120, 150, 130, 140]).repeat(6).tolist() + \
        np.array([130]).repeat(68).tolist()
    # sig5 = [120]
    # print(120)
    # for _ in range(1, 240):
    #     r = nrd(0, 2.5)
    #     nhr = sig5[-1] + r
    #     sig5.append(nhr if 110 < nhr < 160 else nhr - r)
    #     print(int(sig5[-1]))
    # sig5 = list(map(int, sig5))
    # hrs = sig5

    hrs = sig6 = [int(nrd(110, 1)) for _ in range(12 * 10)] + \
                 [110, 110, 110, 145, 150] + [int(nrd(150, dv)) for _ in range(12)] + \
                 [150, 140, 135, 130, 125, 120, 110] + \
                 [int(nrd(110, dv)) for _ in range(12 * 2)] + \
                 [int(nrd(125, dv)) for _ in range(12 * 2)] + \
                 [130, 140, 150, 150, 150, 150, 140, 130, 120, 110, 110, 110] + \
                 [int(nrd(110, dv)) for _ in range(12 * 1)] + \
                 [110, 140, 150, 150, 150, 150, 140, 130, 120, 110, 110, 110] + \
                 [int(nrd(110, dv)) for _ in range(12 * 1)]

    signal = (np.random.random(len(hrs) * 5 * Tone.SAMPLE_RATE) - .5)
    # np.sin(np.linspace(0, 2 * np.pi * 1000 * 1200, len(hrs) * 5 * Tone.SAMPLE_RATE)) / 2
    signal = np.zeros(len(hrs) * 5 * Tone.SAMPLE_RATE)
    index = 0
    for i, hr in enumerate(hrs):
        delay_sample_no = int(60 / hr * Tone.SAMPLE_RATE)
        while index < 5 * Tone.SAMPLE_RATE * (i + 1):
            signal[index:index + Tone.sample_no] = signal[index:index + Tone.sample_no] + Tone.tone
            index += delay_sample_no

    # plt.plot(signal)
    # plt.show()

    wav.write("pulses.wav", Tone.SAMPLE_RATE, signal)
    sd.play(signal, Tone.SAMPLE_RATE, blocking=True)


def run(online=True):
    if online:
        global HR, RUN
        RUN = True
        t = Thread(target=online_generator, daemon=True)
        t.start()
        try:
            while RUN:
                inp = input(">")
                if inp.isdigit():
                    HR = int(inp)
                elif inp == 'q':
                    RUN = False
        except KeyboardInterrupt:
            RUN = False
    else:
        offline_generator()


if __name__ == '__main__':
    run(False)
