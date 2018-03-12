import mxnet as mx
import numpy as np
import logging

batch_size = 100
new_height =32
new_weight =32
channel = 1
begin_epoch = 1
num_epoch = 500


def Conv(data, num_filter=1, kernel=(1, 1), stride=(1, 1), pad=(0, 0),  name=None, suffix='',pooling_type = "avg"):
	conv = mx.sym.Convolution(data=data, num_filter=num_filter, kernel=kernel,  stride=stride, pad=pad, no_bias=True, name='%s%s_conv2d' %(name, suffix))
	bn = mx.sym.BatchNorm(data=conv, name='%s%s_batchnorm' %(name, suffix), fix_gamma=True)
	act = mx.sym.Activation(data=bn, act_type='relu', name='%s%s_relu' %(name, suffix))
	res = mx.symbol.Pooling(data=act, kernel=(3,3), pool_type= pooling_type, stride=(2,2), name='pool')
	return res

def get_symbol(data, labels):
	conv1 = Conv (data = data ,num_filter = 32,kernel=(5,5),stride = (1,1) , pad = (2,2) ,name = 'conv1',pooling_type = 'max')
	conv2 = Conv (data = conv1 ,num_filter = 32 ,kernel=(3,3),stride = (1,1) , pad = (1,1) ,name = 'conv2',pooling_type = 'avg')
	conv3 = Conv (data = conv2 ,num_filter = 16 ,kernel=(3,3),stride = (1,1) , pad = (1,1) ,name = 'conv3',pooling_type = 'max')
	#conv4 = Conv (data = conv3 ,num_filter = 16 ,kernel=(3,3),stride = (1,1) , pad = (1,1) ,name = 'conv4',pooling_type = 'avg')

	flat = mx.symbol.Flatten(data= conv3)
	fc = mx.symbol.FullyConnected(data=flat, num_hidden=2, name='fc')
	softmax = mx.symbol.SoftmaxOutput(data=fc, label=labels,name='softmax')

	return softmax


#training data and testing data
train_data_iter = mx.io.ImageRecordIter(
	path_imgrec='/data/zhaoxu.li/smoke_data/mx_data/0307_data/train.rec',
	data_shape=(channel,new_height,new_weight),
	batch_size=batch_size
	)

eval_data_iter = mx.io.ImageRecordIter(
	path_imgrec='/data/zhaoxu.li/smoke_data/mx_data/0307_data/test.rec',
	data_shape=(channel,new_height,new_weight),
	batch_size=batch_size
	)

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

#save model
model_prefix = './models/model'
checkpoint = mx.callback.do_checkpoint(model_prefix)

#network
data = mx.symbol.Variable('data')
labels = mx.symbol.Variable('softmax_label')
net = get_symbol(data, labels)

solver = mx.mod.Module(symbol=net, data_names=['data'], label_names=['softmax_label'], context=mx.gpu(1))
solver.fit(
    train_data=train_data_iter,
           eval_data=eval_data_iter,
           eval_metric=['acc','CrossEntropy'],
           #eval_metric='mse',
	       epoch_end_callback=checkpoint,
           optimizer='sgd',
	       optimizer_params=
           {'learning_rate' : 0.0001,
            'momentum' : 0.9,
		   'lr_scheduler' : mx.lr_scheduler.FactorScheduler(step=10000, factor=0.5),
		   'wd' : 0.004
           },
           begin_epoch=begin_epoch, num_epoch=num_epoch,
           #initializer= mx.initializer.Normal(sigma=0.01),
	       )

#score = solver.score(eval_data_iter,'mse')
score = solver.score(eval_data_iter, ['mse','acc'])
