# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_Process_object demo_process'] = GenericRepr('Process(func=test_func; ptype=ProcessType.STANDARD; comment="This is the process comment"; gate=True; group=None; config_inputs={\'config.a\': \'x\'}; parameters_inputs={}; external_state_inputs={}; additional_inputs={\'10\': \'z\'}; state_inputs={\'state.a\': \'y\'}; state_outputs={\'result\': \'state.x\'}; args=[])')

snapshots['test_process_object_human demo_process_human'] = {
    'additional_inputs': {
        '10': 'z'
    },
    'args': [
    ],
    'comment': 'This is the process comment',
    'config_inputs': {
        'config.a': 'x'
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
        'state.a': 'y'
    },
    'state_outputs': {
        'result': 'state.x'
    }
}
