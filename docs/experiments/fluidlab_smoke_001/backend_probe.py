import json
import taichi as ti
try:
 ti.init(arch=ti.gpu,device_memory_GB=8,packed=True)
 x=ti.field(dtype=ti.f32,shape=4)
 @ti.kernel
 def run():
  for i in x:x[i]=i*i
 run()
 report={'requested':'ti.gpu','actual_backend':str(ti.lang.impl.current_cfg().arch),'values':x.to_numpy().tolist(),'taichi_version':ti.__version__}
 print(json.dumps(report))
 with open('/out/backend.json','w') as f:json.dump(report,f,indent=2)
except Exception as exc:
 with open('/out/backend-error.json','w') as f:json.dump({'error':str(exc),'type':type(exc).__name__},f,indent=2)
 raise
