"""Offline integrity/static checks; never imports or executes FluidLab code."""
import ast
from decimal import Decimal
import hashlib
import json
from pathlib import Path
import yaml

HERE=Path(__file__).resolve().parent


def check():
    profile=json.loads((HERE/'reproduction-profile.json').read_text())
    sources=HERE/'source-snapshots'
    for item in profile['files']:
        raw=(sources/item['path']).read_bytes()
        if hashlib.sha256(raw).hexdigest()!=item['sha256']:
            raise ValueError('Pinned file hash mismatch: '+item['path'])
    env=ast.parse((sources/'fluidlab/envs/pouring_env.py').read_text())
    cls=next(n for n in env.body if isinstance(n,ast.ClassDef) and n.name=='PouringEnv')
    constructor=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    args={a.arg for a in constructor.args.args}
    launcher=ast.parse((sources/'fluidlab/run.py').read_text())
    calls=[n for n in ast.walk(launcher) if isinstance(n,ast.Call) and isinstance(n.func,ast.Attribute)
           and isinstance(n.func.value,ast.Name) and n.func.value.id=='gym' and n.func.attr=='make']
    unexpected=sorted({k.arg for c in calls for k in c.keywords if k.arg is not None and k.arg not in args})
    cfg=yaml.safe_load((sources/'fluidlab/configs/exp_pouring.yaml').read_text())
    selected=profile['candidate_settings']
    assert cfg['EXP']['env_name']==selected['env'] and cfg['EXP']['seed']==selected['seed']
    assert cfg['SOLVER']['n_iters']==selected['iterations']
    assert cfg['SOLVER']['optim']['type']==selected['optimizer']
    assert Decimal(str(cfg['SOLVER']['optim']['lr']))==Decimal(selected['learning_rate'])
    assert selected['substeps']*Decimal(selected['simulation_dt_code_units'])==Decimal(selected['nominal_step_code_units'])
    # Independently check that the proposed patch has a parseable target and fixes
    # precisely this keyword mismatch; this does not test runtime rendering.
    original=(sources/'fluidlab/envs/pouring_env.py').read_text()
    patch=(HERE/'proposed-renderer-compatibility.patch').read_text()
    output=[];cursor=0;lines=original.splitlines(keepends=True)
    import re
    for hunk in patch.split('@@ ')[1:]:
        if not hunk.startswith('-'):continue
        header,body=hunk.split(' @@\n',1)
        start=int(re.match(r'-(\d+)',header).group(1))-1
        output.extend(lines[cursor:start]);cursor=start
        for line in body.splitlines(keepends=True):
            if line.startswith(' '):
                assert lines[cursor]==line[1:];output.append(line[1:]);cursor+=1
            elif line.startswith('-'):assert lines[cursor]==line[1:];cursor+=1
            elif line.startswith('+'):output.append(line[1:])
    output.extend(lines[cursor:]);patched=ast.parse(''.join(output))
    patched_cls=next(n for n in patched.body if isinstance(n,ast.ClassDef) and n.name=='PouringEnv')
    patched_init=next(n for n in patched_cls.body if isinstance(n,ast.FunctionDef) and n.name=='__init__')
    patched_args={a.arg for a in patched_init.args.args}
    assert set(unexpected)<=patched_args
    assert 'type=self.renderer_type' in ''.join(output)
    assert profile['readiness']['execution_eligible'] is False
    return {'pinned_file_count':len(profile['files']),'hash_checks':'PASS','configuration_checks':'PASS',
        'code_time_arithmetic':'PASS','unexpected_launcher_keywords':unexpected,
        'patch_applies_and_parses':True,'patch_runtime_tested':False,
        'native_runtime_verified':False,'paper_experiment_match':'unverified',
        'physical_unit_scale_status':'unestablished','execution_eligible':False,
        'scope':'Static evidence only; no FluidLab code was executed and no paper result was reproduced.'}


if __name__=='__main__':
    report=check()
    (HERE/'static-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
