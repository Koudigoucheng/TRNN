"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, noise_amplitude=0.1, expected_snr=10, normalize_flag=False):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Set Signal Amplitude',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.noise_amplitude = noise_amplitude
	self.expected_snr = expected_snr
	self.normalize_flag = normalize_flag

    def work(self, input_items, output_items):
        """example: multiply with constant""" 
	# print len(input_items) # 1, The input is a list of length 1
	# print type(input_items[0]) # np.array, The elements of the list are matrices of varying length, and each element of the matrix is a complex number
	output_items[0][:] = input_items[0]
	if self.normalize_flag:
		each_sample_signal_power = np.real(input_items[0] * np.conj(input_items[0]))
		signal_average_power = np.mean(each_sample_signal_power)
		noise_average_power = self.noise_amplitude * self.noise_amplitude
		expected_power_of_output_signal = noise_average_power * (10 ** (self.expected_snr/10.0))
		# print input_items[0][0], np.conj(input_items[0][0]), signal_average_power, expected_power_of_output_signal
		output_items[0][:] = input_items[0] * np.sqrt(expected_power_of_output_signal / signal_average_power)

		each_output_signal_power = np.real(output_items[0] * np.conj(output_items[0]))
		output_signal_average_power = np.mean(each_output_signal_power)
		actual_snr = round(10 * np.log10(output_signal_average_power / noise_average_power), 2)
		# print output_items[0][0], np.conj(output_items[0][0]), output_signal_average_power
		print 'Expected SNR:', self.expected_snr, 'Actual SNR:', actual_snr
		
        return len(output_items[0])
