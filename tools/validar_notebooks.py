"""Ejecutar desde un entorno con dependencias del proyecto, nbclient e ipykernel."""
from pathlib import Path
import json,sys,time
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
ROOT=Path(__file__).resolve().parents[1]
results=[]
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    book=nbformat.read(path,as_version=4)
    manager=KernelManager(kernel_name='python3')
    manager.kernel_spec.argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}']
    started=time.perf_counter()
    try:
        NotebookClient(book,timeout=600,km=manager,resources={'metadata':{'path':str(ROOT)}}).execute()
        nbformat.write(book,path)
        results.append({'notebook':path.name,'executed':True,'seconds':round(time.perf_counter()-started,2),'code_cells':sum(c.cell_type=='code' for c in book.cells)})
        print('PASS',path.name,flush=True)
    finally:
        if manager.has_kernel:manager.shutdown_kernel(now=True)
(ROOT/'tools/notebook_validation.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
