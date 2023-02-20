# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_Process_object demo_process'] = GenericRepr('Process(func=test_func; ptype=ProcessType.STANDARD; comment="This is the process comment"; gate=True; group=None; config_inputs={\'x\': \'config.a\'}; parameters_inputs={}; external_state_inputs={}; additional_inputs={\'z\': \'10\'}; state_inputs={\'y\': \'state.a\'}; state_outputs={\'result\': \'state.x\'}; args=[])')

snapshots['test_process_object_human demo_process_human'] = {
    'additional_inputs': {
        'z': '10'
    },
    'args': [
    ],
    'comment': 'This is the process comment',
    'config_inputs': {
        'x': 'config.a'
    },
    'external_state_inputs': {
    },
    'func': 'test_func',
    'gate': True,
    'group': None,
    'parameters_inputs': {
    },
    'ptype': GenericRepr('<ProcessType.STANDARD: 0>'),
    'state_inputs': {
        'y': 'state.a'
    },
    'state_outputs': {
        'result': 'state.x'
    }
}
