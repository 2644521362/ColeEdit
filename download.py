import os
import json
import shutil
idx = 0

init = '/openseg_blob/PD/Crello_v2/benchmark_init_text2typo'
png_url = '/openseg_blob/PD/Crello_v2/benchmark_init_if'
for t in os.listdir(init):
    subDir = os.path.join(init,t)
    t_idx =0
    if t.endswith('.zip'):
        continue
    for item in os.listdir(subDir):
        if not item.endswith('.json'):
            continue
        t_idx+=1
        template_id = item.split('.')[0]
        jsonFile = os.path.join(subDir,item)
        pngFile = os.path.join(png_url,t)
        shutil.copy(jsonFile,f'/openseg_blob/PD/lcx/streamlit/resources/jsons/{t}_{t_idx}.json')
        shutil.copy(os.path.join(init,t,f'{template_id}_pred.png'),f'/openseg_blob/PD/lcx/streamlit/resources/init_pngs/{t}_{t_idx}.png')


        shutil.copy(os.path.join(pngFile,f'{template_id}_bg.png'),f'/openseg_blob/PD/lcx/streamlit/resources/pngs/{t}_{t_idx}_bg.png')
        shutil.copy(os.path.join(pngFile,f'{template_id}_obj.png'),f'/openseg_blob/PD/lcx/streamlit/resources/pngs/{t}_{t_idx}_obj.png')
        if t_idx>20:
            break
    print(t," : ",t_idx)
creative_url = '/openseg_blob/PD/Crello_v2/creative_init_text2typo'
c_idx = 0
for item in os.listdir(creative_url):
    if not item.endswith('.json'):
        continue
    c_idx+=1
    
    filename = item.split('.')[0]
    jsonFile = os.path.join(creative_url,item)
    shutil.copy(os.path.join(creative_url,f'{filename}_pred.png'),f'/openseg_blob/PD/lcx/streamlit/resources/init_pngs/Creative_{c_idx}.png')
    
    shutil.copy(jsonFile,f'/openseg_blob/PD/lcx/streamlit/resources/jsons/Creative_{c_idx}.json')
    shutil.copy(f'/openseg_blob/PD/Crello_v2/creative_init_if/{filename}_bg.png',f'/openseg_blob/PD/lcx/streamlit/resources/pngs/Creative_{c_idx}_bg.png')
    shutil.copy(f'/openseg_blob/PD/Crello_v2/creative_init_if/{filename}_obj.png',f'/openseg_blob/PD/lcx/streamlit/resources/pngs/Creative_{c_idx}_obj.png')
    if c_idx>20:
        break