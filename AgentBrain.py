'''Agent's brain (CNN architecture)'''

import tensorflow as tf
from settings import ArchitectureSetting, AgentSetting

class Brain(object):
	
	def __init__(self, num_action, dueling = False, training = True):

		self.dueling = dueling
		#params initializers
		self.w_inii = tf.contrib.layers.xavier_initializer(uniform=True, seed=None, dtype=tf.float32)
	
		self.b_inii = tf.constant_initializer(0.0)
		
		
		self.net_input = ArchitectureSetting.in_shape
		
		self.l1_filters = ArchitectureSetting.f1_no

		self.l1_filt_size = ArchitectureSetting.f1_size
		
		self.l1_strd = ArchitectureSetting.stride1

		self.shp1 = [ self.l1_filt_size[0],self.l1_filt_size[1], self.net_input[2], self.l1_filters ]
		
		#l1 map = 21x21x32
		
		self.l2_filters  = ArchitectureSetting.f2_no 
		
		self.l2_filt_size = ArchitectureSetting.f2_size 
		
		self.l2_strd = ArchitectureSetting.stride2

		
		self.shp2 = [ self.l2_filt_size[0],self.l2_filt_size[1], self.l1_filters, self.l2_filters ]	

		#l2 map = 11x11x64

		self.l3_filters  = ArchitectureSetting.f3_no 
		
		self.l3_filt_size = ArchitectureSetting.f3_size

		self.l3_strd = ArchitectureSetting.stride3
 

		self.shp3 = [ self.l3_filt_size[0], self.l3_filt_size[1], self.l2_filters, self.l3_filters ]

		#l3 map = 11x11x64

		self.l4_nodes = ArchitectureSetting.nodes

		self.shp4 = [ 11*11*64, self.l4_nodes]

		self.out_actions = num_action
		
		self.shOut = [self.l4_nodes, self.out_actions]

		#duel stuff
		self.shOutValueScalar = 1 #scalar output
		self.shOutDuelValue = [self.l4_nodes,self.shOutValueScalar]

		self.nn_input = tf.placeholder(tf.float32, shape=[ None,self.net_input[0],self.net_input[1],self.net_input[2] ])

		self.batch_size = AgentSetting.minibatch
		
		with tf.variable_scope('Q_net_paras'):
				
			self.Q_l1_w = tf.get_variable(name = 'Q_w1', shape = self.shp1, dtype = tf.float32,initializer = self.w_inii,trainable = True)
			self.Q_l1_b = tf.get_variable(name = 'Q_b1', shape = self.l1_filters, dtype = tf.float32,initializer = self.b_inii,trainable = True)
			self.Q_l2_w = tf.get_variable(name = 'Q_w2', shape = self.shp2, dtype = tf.float32,initializer = self.w_inii,trainable = True)
			self.Q_l2_b = tf.get_variable(name = 'Q_b2', shape = self.l2_filters, dtype = tf.float32,initializer = self.b_inii,trainable = True)
			self.Q_l3_w = tf.get_variable(name = 'Q_w3', shape = self.shp3, dtype = tf.float32,initializer = self.w_inii,trainable = True)
			self.Q_l3_b = tf.get_variable(name = 'Q_b3', shape = self.l3_filters, dtype = tf.float32,initializer = self.b_inii,trainable = True)

			pass #single FC or dueling
			if dueling:
				#value paras beta
				self.Q_l4_wValue = tf.get_variable(name='Q_w4_Value', shape=self.shp4, dtype=tf.float32, initializer=self.w_inii,
											  trainable=True)
				self.Q_l4_bValue = tf.get_variable(name='Q_b4_Value', shape=self.l4_nodes, dtype=tf.float32,
											  initializer=self.b_inii, trainable=True)
				#advantage paras alpha
				self.Q_l4_wAdv = tf.get_variable(name='Q_w4_Adv', shape=self.shp4, dtype=tf.float32, initializer=self.w_inii,
											  trainable=True)
				self.Q_l4_bAdv = tf.get_variable(name='Q_b4_Adv', shape=self.l4_nodes, dtype=tf.float32,
											  initializer=self.b_inii, trainable=True)

				# OUT -> value is scalar
				self.Q_lOut_wValue = tf.get_variable(name='Q_wOut_Value', shape=self.shOutDuelValue, dtype=tf.float32,
												initializer=self.w_inii, trainable=True)
				self.Q_lOut_bValue = tf.get_variable(name='Q_bOut_Value', shape=self.shOutValueScalar, dtype=tf.float32,
												initializer=self.b_inii, trainable=True)

				# OUT -> advantage action dims
				self.Q_lOut_wAdv = tf.get_variable(name='Q_wOut_Adv', shape=self.shOut, dtype=tf.float32,
												initializer=self.w_inii, trainable=True)
				self.Q_lOut_bAdv = tf.get_variable(name='Q_bOut_Adv', shape=self.out_actions, dtype=tf.float32,
												initializer=self.b_inii, trainable=True)

				pass

			else:
				self.Q_l4_w = tf.get_variable(name = 'Q_w4', shape = self.shp4, dtype = tf.float32,initializer = self.w_inii,trainable = True)
				self.Q_l4_b = tf.get_variable(name = 'Q_b4', shape = self.l4_nodes, dtype = tf.float32,initializer = self.b_inii,trainable = True)

				#OUT
				self.Q_lOut_w = tf.get_variable(name = 'Q_wOut', shape = self.shOut, dtype = tf.float32,initializer = self.w_inii,trainable = True)
				self.Q_lOut_b = tf.get_variable(name = 'Q_bOut', shape = self.out_actions, dtype = tf.float32,initializer = self.b_inii,trainable = True)

		'''Initialize T-net weights with those of q-net'''
		if(training):
			with tf.variable_scope("T_net_paras"):
				
				self.T_l1_w = tf.get_variable(name = 'T_w1', dtype = tf.float32,initializer = self.Q_l1_w.initialized_value(),trainable = False)
				self.T_l1_b = tf.get_variable(name = 'T_b1', dtype = tf.float32,initializer = self.Q_l1_b.initialized_value(),trainable = False)
				self.T_l2_w = tf.get_variable(name = 'T_w2', dtype = tf.float32,initializer = self.Q_l2_w.initialized_value(),trainable = False)
				self.T_l2_b = tf.get_variable(name = 'T_b2', dtype = tf.float32,initializer = self.Q_l2_b.initialized_value(),trainable = False)
				self.T_l3_w = tf.get_variable(name = 'T_w3', dtype = tf.float32,initializer = self.Q_l3_w.initialized_value(),trainable = False)
				self.T_l3_b = tf.get_variable(name = 'T_b3', dtype = tf.float32,initializer = self.Q_l3_b.initialized_value(),trainable = False)

				pass  # single FC or dueling
				if dueling:
					# value paras beta
					self.T_l4_wValue = tf.get_variable(name='T_w4_Value', dtype=tf.float32,
												  initializer=self.Q_l4_wValue.initialized_value(), trainable=False)
					self.T_l4_bValue = tf.get_variable(name='T_b4_Value', dtype=tf.float32,
												  initializer=self.Q_l4_bValue.initialized_value(), trainable=False)
					# advantage paras alpha
					self.T_l4_wAdv = tf.get_variable(name='T_w4_Adv', dtype=tf.float32,
												  initializer=self.Q_l4_wAdv.initialized_value(), trainable=False)
					self.T_l4_bAdv = tf.get_variable(name='T_b4_Adv', dtype=tf.float32,
												  initializer=self.Q_l4_bAdv.initialized_value(), trainable=False)

					# OUT -> value is scalar
					self.T_lOut_wValue = tf.get_variable(name='T_wOut_Value', dtype=tf.float32,
													initializer=self.Q_lOut_wValue.initialized_value(), trainable=False)
					self.T_lOut_bValue = tf.get_variable(name='T_bOut_Value', dtype=tf.float32,
													initializer=self.Q_lOut_bValue.initialized_value(), trainable=False)
					# OUT -> advantage action dims
					self.T_lOut_wAdv = tf.get_variable(name='T_wOut_Adv', dtype=tf.float32,
													initializer=self.Q_lOut_wAdv.initialized_value(), trainable=False)
					self.T_lOut_bAdv = tf.get_variable(name='T_bOut_Adv', dtype=tf.float32,
													initializer=self.Q_lOut_bAdv.initialized_value(), trainable=False)

					pass

				else:

					self.T_l4_w = tf.get_variable(name = 'T_w4', dtype = tf.float32,initializer = self.Q_l4_w.initialized_value(),trainable = False)
					self.T_l4_b = tf.get_variable(name = 'T_b4', dtype = tf.float32,initializer = self.Q_l4_b.initialized_value(),trainable = False)

					# OUT
					self.T_lOut_w = tf.get_variable(name='T_wOut', dtype=tf.float32,initializer=self.Q_lOut_w.initialized_value(), trainable=False)
					self.T_lOut_b = tf.get_variable(name='T_bOut', dtype=tf.float32,initializer=self.Q_lOut_b.initialized_value(), trainable=False)

				pass


		self._build_net(training)

	#'NWHC' format!
	def _build_net(self,training = True):
		
		self.Q_nn()
		if training:
			self.T_nn()

	
	def _conv2d(self,inn , kernel , strd, bias):
		
		return tf.nn.bias_add(tf.nn.conv2d(inn, kernel , strides=[1, strd, strd, 1], padding ="SAME"), bias)
 
	def _classic_fc(self,inn ,weights, bias):

		return tf.nn.bias_add(tf.matmul(inn, weights),bias)

	'''The advantage of the dueling architecture lies partly in its ability to learn the state-value function efficiently.'''
	def _dueling_archOutput(self,value,advantage):
		# Q = value + (adv - avg.Adv)
		pass
		advAvg = tf.expand_dims( tf.reduce_mean(advantage,axis = 1), axis=1)
		advIdentifiable = tf.subtract(advantage, advAvg)
		Qvalue = tf.add(value, advIdentifiable)
		return Qvalue

	
	def _activation_fn(self, da):

		return tf.nn.relu(da)

	def _flatten_fn(self,be_flat):

		shape = be_flat.get_shape().as_list()
		result = tf.reshape(be_flat, [-1, shape[1] * shape[2] * shape[3]])
		return result


	def Q_nn(self,forSess = False):

		if not forSess:
			h1 = self._activation_fn(self._conv2d( self.nn_input, self.Q_l1_w, self.l1_strd, self.Q_l1_b ) )

			h2 = self._activation_fn(self._conv2d(h1,self.Q_l2_w, self.l2_strd, self.Q_l2_b))

			h3 = self._activation_fn(self._conv2d(h2,self.Q_l3_w, self.l3_strd , self.Q_l3_b))

			flat_h3 = self._flatten_fn(h3)

			pass
			if self.dueling:

				h4_duelValueIn = self._activation_fn(self._classic_fc(flat_h3, self.Q_l4_wValue, self.Q_l4_bValue))
				h4_duelAdvIn = self._activation_fn(self._classic_fc(flat_h3, self.Q_l4_wAdv, self.Q_l4_bAdv))

				h4_duelValueOut = self._activation_fn(self._classic_fc(h4_duelValueIn, self.Q_lOut_wValue, self.Q_lOut_bValue))
				h4_duelAdvOut = self._activation_fn(self._classic_fc(h4_duelAdvIn, self.Q_lOut_wAdv, self.Q_lOut_bAdv))

				self.qValuePrediction = self._dueling_archOutput(h4_duelValueOut,h4_duelAdvOut)
				pass
			else:
				h4_fc  = self._activation_fn(self._classic_fc(flat_h3, self.Q_l4_w ,self.Q_l4_b))
				self.qValuePrediction = self._classic_fc(h4_fc, self.Q_lOut_w, self.Q_lOut_b)

			pass


		if forSess:
			return self.qValuePrediction
	

	def T_nn(self, forSess = False):

		if not forSess:
			h1 = self._activation_fn(self._conv2d(self.nn_input, self.T_l1_w, self.l1_strd, self.T_l1_b))

			h2 = self._activation_fn(self._conv2d(h1,    self.T_l2_w, self.l2_strd, self.T_l2_b))

			h3 = self._activation_fn(self._conv2d(h2,    self.T_l3_w, self.l3_strd, self.T_l3_b))

			flat_h3 = self._flatten_fn(h3)

			pass
			if self.dueling:

				h4_duelValueIn = self._activation_fn(self._classic_fc(flat_h3, self.T_l4_wValue, self.T_l4_bValue))
				h4_duelAdvIn = self._activation_fn(self._classic_fc(flat_h3, self.T_l4_wAdv, self.T_l4_bAdv))

				h4_duelValueOut = self._activation_fn(self._classic_fc(h4_duelValueIn, self.T_lOut_wValue, self.T_lOut_bValue))
				h4_duelAdvOut = self._activation_fn(self._classic_fc(h4_duelAdvIn, self.T_lOut_wAdv, self.T_lOut_bAdv))

				self.nxt_qValuePrediction = self._dueling_archOutput(h4_duelValueOut, h4_duelAdvOut)
				pass
			else:
				h4_fc = self._activation_fn(self._classic_fc(flat_h3, self.T_l4_w, self.T_l4_b))
				self.nxt_qValuePrediction = self._classic_fc( h4_fc, self.T_lOut_w ,self.T_lOut_b)
			pass
			self.updateTparas()  # to create tf ops

		if forSess:
			return self.nxt_qValuePrediction
	
	def updateTparas(self,forSess = False):

		if not forSess:

			self.a = self.T_l1_w.assign(self.Q_l1_w)
			self.b = self.T_l1_b.assign(self.Q_l1_b)
			self.c = self.T_l2_w.assign(self.Q_l2_w)
			self.d = self.T_l2_b.assign(self.Q_l2_b)
			self.e = self.T_l3_w.assign(self.Q_l3_w)
			self.f = self.T_l3_b.assign(self.Q_l3_b)
			pass
			if self.dueling:

				self.dgV = self.T_l4_wValue.assign(self.Q_l4_wValue)
				self.dhV = self.T_l4_bValue.assign(self.Q_l4_bValue)

				self.dgA = self.T_l4_wAdv.assign(self.Q_l4_wAdv)
				self.dhA = self.T_l4_bAdv.assign(self.Q_l4_bAdv)

				self.diV = self.T_lOut_wValue.assign(self.Q_lOut_wValue)
				self.djV = self.T_lOut_bValue.assign(self.Q_lOut_bValue)

				self.diA = self.T_lOut_wAdv.assign(self.Q_lOut_wAdv)
				self.djA = self.T_lOut_bAdv.assign(self.Q_lOut_bAdv)

				pass

			else:
				self.g = self.T_l4_w.assign(self.Q_l4_w)
				self.h = self.T_l4_b.assign(self.Q_l4_b)
				self.i = self.T_lOut_w.assign(self.Q_lOut_w)
				self.j = self.T_lOut_b.assign(self.Q_lOut_b)
			pass

		if forSess:

			if self.dueling:
				return [self.a,self.b,self.c,self.d,self.e,self.f,self.dgV,self.dhV,self.diV,self.djV,self.dgA,self.dhA,self.diA,self.djA]
				pass
			else:
				return [self.a,self.b,self.c,self.d,self.e,self.f,self.g,self.h,self.i,self.j]