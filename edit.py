import streamlit as st  
import json  
from PIL import Image  
import os


from PIL import Image, ImageDraw,ImageFont
import math
import glob  
import time
import skia
import io
import base64
import copy
import numpy as np
from matplotlib import font_manager
import html 
import re




# 从json文件中读取数据 
def is_font_exists(font_name):
    font_list = os.listdir('./font')
    for font in font_list:  
        if font_name.lower().replace(' ','-') in font.lower() or font_name.lower().replace(' ','') in font.lower():  
            return True, font  
    return False, False 
def get_image(bg_path, obj_path, example):
    example = copy.deepcopy(example)
    canvas_width = example['canvas_width']
    canvas_height = example['canvas_height']
    flag = example['layers']['objlayer']['flag']
    scale = 1.0
    surface = skia.Surface(int(scale * canvas_width), int(scale * canvas_height))
    # white background color
    bgimg = Image.open(os.path.join(bg_path))
    objimg = Image.open(os.path.join(obj_path))
    objimg = objimg.resize((500,500))
    # storeimg = Image.open('/openseg_blob/PD/lcx/gpt4vCompare/target/food.png')
    # storeimg = storeimg.resize((500,500))
    with surface as canvas:
        canvas.clear(skia.ColorWHITE)
        
        # bg render
        image = skia.Image.frombytes(
            bgimg.convert('RGBA').tobytes(),
            bgimg.size,
            skia.kRGBA_8888_ColorType)
        rect = skia.Rect.MakeXYWH(0, 0, canvas_width, canvas_height)
        paint = skia.Paint(AntiAlias=True)
        
        with skia.AutoCanvasRestore(canvas):
            canvas.drawImageRect(image, rect, paint=paint)

        # obj render
        # if '1' in flag:
        # image  = skia.Image.frombytes(
        #     storeimg.convert('RGBA').tobytes(),
        #     storeimg.size,
        #     skia.kRGBA_8888_ColorType)
        # rect = skia.Rect.MakeXYWH(100, 600, 400, 400)
        # paint = skia.Paint(AntiAlias=True)
        
        with skia.AutoCanvasRestore(canvas):
            canvas.drawImageRect(image, rect, paint=paint)
            
        image = skia.Image.frombytes(
            objimg.convert('RGBA').tobytes(),
            objimg.size,
            skia.kRGBA_8888_ColorType)
        
        rect = skia.Rect.MakeXYWH(0, 0, canvas_width,canvas_height) #canvas_height)
        # rect = skia.Rect.MakeXYWH(650, 600, 400, 400) #canvas_width,canvas_height)
        paint = skia.Paint(AntiAlias=True)
        
        with skia.AutoCanvasRestore(canvas):
            canvas.drawImageRect(image, rect, paint=paint)
            
        image = surface.makeImageSnapshot()
        data = image.encodeToData()
        render_img= Image.open(io.BytesIO(base64.b64decode(base64.b64encode(data).decode('UTF-8'))))
    return render_img

def RenderText(canvas, textdict):
    
    textdata = textdict
    color = tuple(textdata['color'])
    color = tuple([max(0,min(255,x)) for x in list(color)])
    alpha = 255
    fontname = textdata['font']
    fontsize = textdata['font_size']
    capitalize = textdata['capitalize']
    text_left, text_top, text_width, text_height = textdata['left'], textdata['top'], textdata['width'], textdata['height']
    text_align = textdata['text_align']
    letter_bold = textdata['letter_bold']
    angle = textdata['angle']
    # surface_save = skia.Surface(int(text_width*2),int(text_height*2))
    # canvas_save = surface_save.getCanvas()

    paint = skia.Paint()  
    paint.setAntiAlias(True)  
    paint.setColor(skia.ColorSetARGB(alpha, *color)) 
    # if letter_bold == 1:  
    #     paint.setFakeBoldText(True) 
    if fontname.endswith('.ttf'):
        fontname=fontname[:-4]
    flag, font = is_font_exists(fontname)
   
    
    # print(fontname)
    if not flag:
        print(f'The {fontname} is not exist, Use Arial rather.')
        fontname = 'Arial'
    else:
        pass

    if flag:
        font_path = f"./font/{font}"  # 将此处替换为您的字体文件的绝对路径  
    else:
        font_path = f"./font/ABeeZee-Italic.ttf"
    # typeface = skia.Typeface.MakeFromFile(font_path, skia.FontStyle.Bold())  

    if letter_bold == 1:
        typeface = skia.Typeface.MakeFromFile(font_path)  
    else:
        typeface = skia.Typeface.MakeFromFile(font_path)
    font = skia.Font(typeface, fontsize) 
    text = textdata['text']

    text = html.unescape(text)
    if capitalize == True or capitalize == 1 or capitalize == 'true' :
        text = text.upper() 
 
    lines = text.strip().split('\n')  
    wrapped_lines = []  
        
    for line in lines:  
        words = line.split(' ') 
            
        current_line = []  
    
        for word in words:  
            test_line = ' '.join(current_line + [word])  
            cur_width = font.measureText(test_line)  
            if cur_width <= text_width*1.05 or (((len(wrapped_lines)+1)*font.getSize() / text_height) > (cur_width/text_width)):  
                current_line.append(word)  
            else:  
                wrapped_lines.append(' '.join(current_line))  
                current_line = [word] 
                 
        wrapped_lines.append(' '.join(current_line))  

        text_y = text_top - font.getMetrics().fAscent 
    with skia.AutoCanvasRestore(canvas):
        
        if angle != 0:
            degree = 180. * angle / np.pi
            canvas.rotate(degree, text_left + text_width / 2., text_top + text_height / 2.)   
        y_offset = 0  
        for line in wrapped_lines: 
            if line == '':
                continue

            blob = skia.TextBlob.MakeFromString(line, font)  
            bounds = blob.bounds()
    
            if text_align == "center":  
                text_x = text_left - bounds.x() + (text_width - bounds.width())/ 2 

            elif text_align == "right":  
                text_x = text_left - bounds.x() + (text_width - bounds.width())  
            else:  
                text_x = text_left - bounds.x()   
            canvas.drawString(line, text_x, text_y+y_offset, font, paint)   
            y_offset += font.getSize()  
    return canvas 
def Render2(image, textlist):
    width, height = image.size
    image_np = np.array(image)
    image_np = np.dstack([image_np, np.ones((image_np.shape[0], image_np.shape[1]), dtype='uint8') * 255]) 
    skia_image = skia.Image.fromarray(image_np)
    surface = skia.Surface(int(width), int(height))
    with surface as canvas:
        canvas.drawImage(skia_image, 0, 0)
        for text in textlist:
            RenderText(canvas, text)
        image = surface.makeImageSnapshot()
        data = image.encodeToData()   
        
        # with open('/openseg_blob/PD/lcx/gpt4vCompare/modiy/onlytest.png', 'wb') as file:  
        #     file.write(data)
        render_img= Image.open(io.BytesIO(base64.b64decode(base64.b64encode(data).decode('UTF-8'))))
    return render_img 
def pipeline(dat,bg,obj):
    
    
    # bg_obj_url = bgurl
        
        # for k in new_map:
        #     if new_map[k]==int(fid):
        #         template_new_id = k

    bgobjimage = get_image(bg,obj,dat)
    bgobjimage = bgobjimage.convert('RGB').resize((dat['canvas_width'],dat['canvas_height']))
    # draw = ImageDraw.Draw(bgobjimage)
    textlist = []
    for d in dat['layers']['textlayer']:
        for item in dat['layers']['textlayer'][d]:
            item['left'] = item['left']#*dat['canvas_width']
            item['top'] = item['top']#*dat['canvas_height']
            item['width'] =item['width']#dat['canvas_width']
            item['height']=item['height'] #dat['canvas_height']
            # item['opacity'] = 255
            textlist.append(item)

    img = Render2(bgobjimage, textlist)
    return img
   

st.set_page_config(layout='wide')  


pick_item_list_all = os.listdir('./new_resources/jsons')
pick_item_list = []
for item in pick_item_list_all:
    pick_item_list.append(item.split('.')[0])
pick_item_list = sorted(pick_item_list)
selected_item = st.selectbox('Select a item: ', options=pick_item_list)  
selected_item_index = selected_item.split('.')[0] 
saved_json_path = f'./workspace/{selected_item_index}_cur.json'  

if 'selected_item' in st.session_state and st.session_state.selected_item == selected_item:
    if  'cur_json' in st.session_state and st.session_state.cur_json !=-1 :
        data = st.session_state.cur_json
    else: 
        with open(f'./new_resources/jsons/{selected_item_index}.json', 'r') as f:    
            data = json.load(f)  
        
else:  
        # 如果不存在，就加载默认的json  
    with open(f'./new_resources/jsons/{selected_item_index}.json', 'r') as f:    
        data = json.load(f)  
        data_orin = data.copy()
    st.session_state.cur_json=-1
    st.session_state.selected_item = selected_item  
    st.session_state.cur_result = Image.open(f'./new_resources/init_pngs/{selected_item_index}.png')  
    st.session_state.cur_result.resize((1024,1024))    
        
# 创建一个字典来保存用户输入的数据  

# left_column, right_column = st.columns(2)  
t_body = data['layers']['textlayer']['body']
t_head = data['layers']['textlayer']['heading']
t_subhead = data['layers']['textlayer']['subheading']
totaly_editable = len(t_body)+len(t_head)+len(t_subhead)
data_new = {}
for idx,body in enumerate(t_body):
    if len(body['text'])<=1:
        continue
    data_new.update({f"body-{idx}":body})
for idx,body in enumerate(t_head):
    if len(body['text'])<=1:
        continue
    data_new.update({f"heading-{idx}":body})
for idx,body in enumerate(t_subhead):
    if len(body['text'])<=1:
        continue
    data_new.update({f"subheading-{idx}":body})

data_new_show_list = []
for item in data_new:
    preview_text = data_new[item]['text'].split(' ')[0]
    data_new_show_list.append(item+" ("+preview_text)

data_new_show_list = sorted(data_new_show_list)
selected_name = st.selectbox('Select a name: ', options=data_new_show_list)  
selected_name=selected_name.split(' (')[0]
selected_dict = data_new[selected_name]  
  
user_inputs = {}  
  

left_column1, left_column2, right_column = st.columns([1,1,2])  
  
image_placeholder = right_column.empty()  
align_options = ['left','center','right']
text_options = sorted(os.listdir('./font'))
text_dict = {}
for idx,text in enumerate(text_options):
    text_dict.update({text:idx})
options = {'text_align':align_options,
           'font':text_options}
# if 'selected_item' not in st.session_state or st.session_state.selected_item != selected_item:  
#     st.session_state.selected_item = selected_item
#     st.session_state.cur_json = -1  
#     st.session_state.cur_result = Image.open(f'./new_resources/init_pngs/{selected_item_index}.png')  
#     st.session_state.cur_result.resize((1024,1024))    
    

image_placeholder.image(st.session_state.cur_result, caption='Generated Image.', use_column_width=True)  
for key, value in selected_dict.items():  
    left_column1.text(f'{key}: {value}')  
    if key in ['text_align','font']:
        if key == 'font':
            cur_font = selected_dict['font']
            flag,fontname = is_font_exists(cur_font)
            selected_dict[key] = left_column2.selectbox(f'New  {key}: ', options[key],index=text_dict[fontname],format_func=lambda x: x)  
        else:
            selected_dict[key] = left_column2.selectbox(f'New  {key}: ', options[key],format_func=lambda x: x)  
    else:
        selected_dict[key] = left_column2.text_input(f'New  {key}: ', value)  
  
if st.button('Submit'):  

    selected_dict['font_size'] = float(selected_dict['font_size'])
    selected_dict['angle'] = float(selected_dict['angle'])
    selected_dict['letter_bold'] = int(selected_dict['letter_bold'])
    selected_dict['letter_spacing'] = float(selected_dict['letter_spacing'])
    selected_dict['width'] = float(selected_dict['width'])
    selected_dict['height'] = float(selected_dict['height'])
    selected_dict['left'] = float(selected_dict['left'])
    selected_dict['top'] = float(selected_dict['top'])
    selected_dict['opacity'] = float(selected_dict['opacity'])
    selected_dict['color'] = eval(selected_dict['color'])
    new_json = data.copy()
    text_type = selected_name.split('-')[0]
    text_index = selected_name.split('-')[1]
    new_json['layers']['textlayer'][text_type][int(text_index)]=selected_dict
    # with open(saved_json_path, 'w') as f:  
    #     json.dump(new_json, f)  
    basic_image = pipeline(new_json,f'./new_resources/pngs/{selected_item_index}_bg.png',f'./new_resources/pngs/{selected_item_index}_obj.png')  
    basic_image.resize((1024,1024))  
    st.session_state.cur_result = basic_image  
    st.session_state.cur_json = new_json
    image_placeholder.image(st.session_state.cur_result, caption='Generated Image.', use_column_width=True) 
