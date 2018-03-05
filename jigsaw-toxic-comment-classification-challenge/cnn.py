import mxnet as mx
import mxnet.ndarray as nd
import mxnet.gluon.nn as nn

class Transpose(nn.HybridBlock):
    def __init__(self, spec, **kwargs):
        super(Transpose, self).__init__(**kwargs)
        self.spec = spec

    def hybrid_forward(self, F, x):
        return F.transpose(x, self.spec)

class Model(object):
    def __init__(self, vsize, ctx='cpu', file=None):
        self.ctx = mx.cpu() if ctx != 'gpu' else mx.gpu()

        self.net = nn.HybridSequential()
        with self.net.name_scope():
            self.net.add(
                nn.Embedding(vsize, 256),
                Transpose((0, 2, 1)),

                nn.Conv1D(256, kernel_size=5, padding=2, activation='relu'),
                nn.MaxPool1D(pool_size=2, strides=2),

                nn.Conv1D(256, kernel_size=3, padding=1, activation='relu'),
                nn.Conv1D(256, kernel_size=3, padding=1, activation='relu'),
                nn.MaxPool1D(pool_size=2, strides=2),

                nn.Conv1D(256, kernel_size=3, padding=1, activation='relu'),
                nn.Conv1D(256, kernel_size=3, padding=1, activation='relu'),
                nn.MaxPool1D(pool_size=2, strides=2),

                nn.Conv1D(256, kernel_size=3, padding=1, activation='relu'),
                nn.Conv1D(256, kernel_size=3, padding=1, activation='relu'),
                nn.GlobalMaxPool1D(),

                nn.Flatten(),
                nn.Dense(6)
            )

        if file != None:
            self.net.load_params(file, ctx=self.ctx)
        else:
            self.net.initialize(ctx=self.ctx)

        self.net.hybridize()

    def train(self, x, y, lr):
        trainer = mx.gluon.Trainer(self.net.collect_params(), 'sgd', {'learning_rate': lr})
        loss = mx.gluon.loss.SigmoidBinaryCrossEntropyLoss()
        x, y = nd.array(x, self.ctx), nd.array(y, self.ctx)
        with mx.autograd.record():
            p = self.net(x)
            L = loss(p, y).mean()
        L.backward()
        trainer.step(1)
        return L.asscalar()

    def predict(self, x):
        return self.net(nd.array(x, self.ctx)).asnumpy()

    def save(self, file):
        return self.net.save_params(file)