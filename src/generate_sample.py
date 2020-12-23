#!/usr/bin/env python3

import json
import os
import numpy as np

import tensorflow as tf

import model, sample, encoder

from flask import Flask, jsonify, request, render_template
app = Flask(__name__)

@app.route('/unconditional-sample', methods=['GET', 'POST'])
def unconditional_sample(
    model_name='117M',
    length=None,
    temperature=1,
    top_k=0
):
    seed = None
    nsamples = 1
    batch_size = 1
    top_p = 0.0

    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        np.random.seed(seed)
        tf.set_random_seed(seed)

        output = sample.sample_sequence(
            hparams=hparams, length=length,
            start_token=enc.encoder['<|endoftext|>'],
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )[:, 1:]

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)
                
        out = sess.run(output)
        text = enc.decode(out[0])
        return jsonify({ 'text':text, 'param-len':length })


@app.route('/conditional-sample', methods=['GET', 'POST'])
def conditional_sample(
    prompt,
    model_name='117M',
    length = None,
    temperature=1,
    top_k=0,
):
    seed = None
    batch_size = 1
    top_p = 0.0

    if batch_size is None:
        batch_size = 1
    assert nsamples % batch_size == 0

    enc = encoder.get_encoder(model_name)
    hparams = model.default_hparams()
    with open(os.path.join('models', model_name, 'hparams.json')) as f:
        hparams.override_from_dict(json.load(f))

    if length is None:
        length = hparams.n_ctx // 2
    elif length > hparams.n_ctx:
        raise ValueError("Can't get samples longer than window size: %s" % hparams.n_ctx)

    with tf.Session(graph=tf.Graph()) as sess:
        context = tf.placeholder(tf.int32, [batch_size, None])
        np.random.seed(seed)
        tf.set_random_seed(seed)
        output = sample.sample_sequence(
            hparams=hparams, length=length,
            context=context,
            batch_size=batch_size,
            temperature=temperature, top_k=top_k, top_p=top_p
        )

        saver = tf.train.Saver()
        ckpt = tf.train.latest_checkpoint(os.path.join('models', model_name))
        saver.restore(sess, ckpt)

        context_tokens = enc.encode(prompt)
        out = sess.run(output, feed_dict={
            context: [context_tokens for _ in range(batch_size)]
        })[:, len(context_tokens):]
        text = enc.decode(out[0])
        return jsonify({'text':text})

@app.route('/test')
def test_page():
    return render_template('index.html')