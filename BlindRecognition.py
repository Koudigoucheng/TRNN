"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr
import h5py
import tensorflow as tf
from keras.models import load_model
import os
import datetime

class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, 
		modulations_list=['BPSK', 'QPSK', '8PSK'],
		rec_data_length=1024,  # Data length for identification
		model_file='/home/lin/workarea/PycharmProjects/gnuradio/mpsk/Blind_Mod_Rec_ResNet.h5',
		work_mode=True,  # if true,recognize
		true_label='QPSK'
		):  # only default arguments here

        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Blind Recognition',   # will show up in GRC
            in_sig=[np.complex64],
            out_sig=[np.int8]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
	self.modulations=modulations_list
	self.rec_data_length=rec_data_length
	self.received_data = []
	self.received_data_length = 0
	self.model_file=model_file
	self.work_mode=work_mode
	self.true_label=true_label
	self.predict_cnt=0
	self.predict_correct_cnt=0
	self.predict_correct_index=self.modulations.index(self.true_label)
	print('self.predict_correct_index',self.predict_correct_index)
	self.predict_accuracy=0
	


	print 'Blind Recognition Work Mode:', self.work_mode   
	# Prevent GPU memory overflow
	if self.work_mode:
		os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
		os.environ['CUDA_VISIBLE_DEVICES'] = "0"  # select gpu,use cpu if -1
		self.config = tf.compat.v1.ConfigProto(allow_soft_placement=True)
		self.config.allow_soft_placement = True
		self.config.gpu_options.per_process_gpu_memory_fraction = 0.8
		self.config.gpu_options.allow_growth = True
		sess = tf.compat.v1.Session(config=self.config)
		print 'loading model from file:', self.model_file
		print("Load Start:",datetime.datetime.now())
		self.model =load_model(self.model_file,compile=False)
		print("Load End:",datetime.datetime.now())

		predict_data = np.zeros((1, 1024, 2), dtype=np.int)
		self.predict_starttime = datetime.datetime.now()
		print("Predict Start:",self.predict_starttime)
		predict = self.model.predict(predict_data)
		self.predict_endtime = datetime.datetime.now()
		predict_list = list(np.squeeze(predict))
		predict = predict_list.index(max(predict_list))
		print('Recognize as:', predict)
		print("Predict End:",self.predict_endtime - self.predict_starttime)

	
    def work(self, input_items, output_items):
        """example: multiply with constant"""
	temp_array = input_items[0][:]
	temp_data_length = len(list(temp_array))
	self.received_data_length = self.received_data_length + temp_data_length
	if not len(self.received_data):  # if self.received_data is null
		self.received_data = temp_array
	else:
		self.received_data = np.concatenate((self.received_data, temp_array), axis=0)
	#print 'received_data_len:', self.received_data_length, 'temp_array.shape:', temp_array.shape, 'self.received_data.shape:', self.received_data.shape
	if self.work_mode:
		if self.received_data_length - self.rec_data_length > 0:
			self.received_data = self.received_data[0:self.rec_data_length]  # (None,) --> (1024,)
			self.received_data = np.expand_dims(self.received_data, axis=-1)  # (1024,) --> (1024,1)
			data_real = np.real(self.received_data)  # (1024,1)
			# print 'data_real:', data_real[0][0]
			data_imag = np.imag(self.received_data)  # (1024,1)
			# print 'data_imag:', data_imag[0][0]
			predicted_data = np.concatenate((data_real, data_imag), axis=1)  # (1024,2)
			predicted_data = np.expand_dims(predicted_data, axis=0)  # (1024,2) --> (1, 1024,2)
			#print 'predicted_data:', predicted_data[0][0][0], predicted_data[0][0][1]

			start_time = datetime.datetime.now()
			print '***********************************************************'
			print 'Predict start:',start_time
			predict = self.model.predict(predicted_data)
			predict_list = list(np.squeeze(predict))
			predict = predict_list.index(max(predict_list))

			self.predict_cnt = self.predict_cnt + 1
			if predict == self.predict_correct_index:
				self.predict_correct_cnt = self.predict_correct_cnt + 1
			
			
			print 'Recognize as:', self.modulations[predict]
			end_time = datetime.datetime.now()			
			print 'Predict end:',end_time
			print 'Using time:',end_time - start_time
			print 'Recognize accuracy:', self.predict_accuracy, '%'
			print '***********************************************************'

			if self.predict_cnt>=1000:
				self.predict_accuracy = round(100.0 * self.predict_correct_cnt/1000.0, 1)
				#self.predict_accuracy = self.predict_correct_cnt
				print 'HHH Recognize accuracy:', self.predict_accuracy, '%'
				self.predict_cnt = 0
				self.predict_correct_cnt = 0
							
			self.received_data = []
			self.received_data_length = 0		

			#data_percent = round(100.0*self.received_data_length/self.max_data_length, 1)
			#print 'count', self.data_count, 'max_length', self.max_data_length, 'data_percent', data_percent, '%', self.start_flag

			#print 'count', self.data_count, 'temp_length', temp_data_length, 'received_length', self.received_data_length, 'max_length', self.max_data_length, 'data_percent', data_percent, '%' 

	#return len(output_items[0])
	return temp_data_length


