"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""
import numpy as np
from gnuradio import gr
import h5py
import os


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, modulations='BPSK_QPSK', label='snr_10db', data_frame=2000,start_flag=False):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Generate Dataset',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.int8]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
	self.modulations=modulations	     
	self.label = label
	self.max_data_length =data_frame * 1024
	self.received_data_length = 0
	self.data_count = 0 
	self.start_flag = start_flag
	
    def work(self, input_items, output_items):
        """example: multiply with constant"""
	if self.start_flag:
		if self.max_data_length - self.received_data_length > 0:
			self.data_count = self.data_count + 1	
			temp_array = input_items[0][:]
			temp_data_length = len(list(temp_array))
			self.received_data_length = self.received_data_length + temp_data_length
			self.filedir = '/home/lin/workarea/PycharmProjects/tensorflow-gpu/ofdm_recognition/1snr/dataset/' + self.modulations + '/' + self.label
			if not os.path.exists(self.filedir):
				os.makedirs(self.filedir)
			self.filename = self.filedir + '/' +  str(self.data_count) + '.h5'
			self.f = h5py.File(self.filename, 'w')
			self.f[self.modulations+self.label] = temp_array
			self.f.close()

			data_percent = round(100.0*self.received_data_length/self.max_data_length, 1)
			print 'count', self.data_count, 'max_length', self.max_data_length, 'data_percent', data_percent, '%', self.start_flag
		else:
			self.start_flag = False			
			self.received_data_length = 0		
			self.data_count = 0
			print 'Data acquisition completed!'


        return len(output_items[0])


