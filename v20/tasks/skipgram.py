#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0103
"""
Skip-gram with negative sampling model/task.
"""
__author__ = "GW [http://gw.tnode.com/] <gw.2015@tnode.com>"
__license__ = "GPLv3+"

from keras.layers.embeddings import Embedding
import numpy as np

from layers.roll import RepeatVector2, RollOffsets, TimeDistributedMerge2


### Model

def skipgram_model(model, ins, max_len, embedding_dim, word2id_size, skipgram_offsets, pre='skipgram'):
    """Skip-gram with negative sampling model as Keras Graph."""

    # context embedding lookup table (sample, time_pad, emb)
    model.add_node(Embedding(word2id_size, embedding_dim, input_length=max_len, init='lecun_uniform'), name=pre + '_emb', input=ins[1])

    # repeat word vectors (sample, time_pad, offset, emb)
    model.add_node(RepeatVector2(len(skipgram_offsets), axis=2), name=pre + '_repeat', input=ins[0])

    # roll context vectors to offsets (sample, time_pad, offset, emb)
    model.add_node(RollOffsets(skipgram_offsets, axis=1), name=pre + '_offsets', input=pre + '_emb')

    # dot product on word-context pairs (sample, time_pad, offset)
    model.add_node(TimeDistributedMerge2(mode='sum', axis=3), name=pre + '_dot', inputs=[pre + '_repeat', pre + '_offsets'], merge_mode='mul')
    return pre + '_dot'


### Encode data

def encode_x1_skipgram(x1_word_pad, skipgram_offsets, max_len):
    """Encode skip-gram labels in binary (sample, time_pad, offset)."""

    # map word pairs with mask to binary skip-gram labels
    pairs = [ [ (x1_word_pad[i] != 0 and x1_word_pad[(i + off) % max_len] != 0)  for off in skipgram_offsets ]  for i in range(max_len) ]
    return np.asarray(pairs)
