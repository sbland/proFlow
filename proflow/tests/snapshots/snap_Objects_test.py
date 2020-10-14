# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import GenericRepr, Snapshot


snapshots = Snapshot()

snapshots['test_Process_object demo_process'] = GenericRepr('Process(func=test_func; ptype=ProcessType.STANDARD; comment="This is the process comment"; gate=True; group=None; config_inputs={\'config.a\': \'x\'}; parameters_inputs={}; external_state_inputs={}; additional_inputs={\'10\': \'z\'}; state_inputs={\'state.a\': \'y\'}; state_outputs={\'result\': \'state.x\'}; args=[])')
