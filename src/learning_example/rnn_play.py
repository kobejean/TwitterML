# encoding: UTF-8
# Copyright 2017 Google.com
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tensorflow as tf
import numpy as np
import my_txtutils

import os

abs_path = os.path.abspath(os.path.dirname(__file__))
checkpoints_path = os.path.join(abs_path, "checkpoints")
latest_checkpoint_path = tf.train.latest_checkpoint(checkpoints_path)
meta_graph_path = latest_checkpoint_path + ".meta"

# these must match what was saved !
ALPHASIZE = my_txtutils.ALPHASIZE
NLAYERS = 3
INTERNALSIZE = 1024

# use topn=10 for all but the last which works with topn=2 for Shakespeare and topn=3 for Python
author = latest_checkpoint_path

def play(count=1000000000, topn=ALPHASIZE):
    ncnt = 0
    with tf.Session() as sess:
        # new_saver = tf.train.import_meta_graph('./rnn_test_minibatchseq_1477670023-174939000.meta')
        new_saver = tf.train.import_meta_graph(meta_graph_path)
        new_saver.restore(sess, author)
        x = my_txtutils.convert_from_alphabet(ord("\n"))
        x = np.array([[x]])  # shape [BATCHSIZE, SEQLEN] with BATCHSIZE=1 and SEQLEN=1

        # initial values
        y = x
        h = np.zeros([1, INTERNALSIZE * NLAYERS], dtype=np.float32)  # [ BATCHSIZE, INTERNALSIZE * NLAYERS]
        for i in range(count):
            yo, h = sess.run(['Yo:0', 'H:0'], feed_dict={'X:0': y, 'pkeep:0': 1., 'Hin:0': h, 'batchsize:0': 1})

            # If sampling is be done from the topn most likely characters, the generated text
            # is more credible and more "english". If topn is not set, it defaults to the full
            # distribution (ALPHASIZE)

            # Recommended: topn = 10 for intermediate checkpoints, topn=2 for fully trained checkpoints

            c = my_txtutils.sample_from_probabilities(yo, topn=topn)
            y = np.array([[c]])  # shape [BATCHSIZE, SEQLEN] with BATCHSIZE=1 and SEQLEN=1
            c = chr(my_txtutils.convert_to_alphabet(c))
            print(c, end="")

            if c == '\n':
                ncnt = 0
            else:
                ncnt += 1
            # if ncnt == 100:
            #     print("")
            #     ncnt = 0

if __name__ == "__main__":
    play(topn=ALPHASIZE)
