# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_Process_object demo_process'] = GenericRepr('Process(func=test_func; comment="This is the process comment"; gate=True; group=None; config_inputs=("config.a, as_=\'x\'",); parameters_inputs=None; external_state_inputs=None; additional_inputs=("10, as_=\'z\'",); state_inputs=("state.a, as_=\'y\'",); state_outputs=[I(from_="_result" as_="x")]; args=[])')
