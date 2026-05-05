import kagglehub
import os
import shutil
# modulo el cual descarga un modelo pre-entrenado desde la web de kaggle, solo se usó una vez
def descargar_modelo_entrenado():
    path = kagglehub.dataset_download("jtaglione/coffee-disease-trained-models")
    
    destino = os.path.join("ia", "models")
    if not os.path.exists(destino):
        os.makedirs(destino)
    
   
    for item in os.listdir(path):
        s = os.path.join(path, item)
        d = os.path.join(destino, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, dirs_exist_ok=True)
        else:
            shutil.copy2(s, d)
            

if __name__ == "__main__":
    descargar_modelo_entrenado()