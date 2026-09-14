"""Ejecutar desde un entorno con dependencias del proyecto, nbclient e ipykernel."""
from pathlib import Path
import nbformat
from nbclient import NotebookClient
ROOT=Path(__file__).resolve().parents[1]
for path in sorted((ROOT/'notebooks').glob('*.ipynb')):
    book=nbformat.read(path,as_version=4)
    NotebookClient(book,timeout=240,kernel_name='python3',resources={'metadata':{'path':str(ROOT)}}).execute()
    nbformat.write(book,path)
    print('PASS',path.name)
