import numpy as np
import pytesseract
import os

white_list = {}
#white_list['name'] = r'-c tessedit_char_whitelist=ß0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghjklmnopqrstuvwxyz_-'
white_list['data'] = r'-c tessedit_char_whitelist=0123456789nrel.,*+-'

def image_to_string(tuple_name, img_path):
    '''Convert the content of a single tuple to a string using Tesseract.
    
    Args:
        tuple_name: The name of a tuple of the PDF table, Please search the file xxx for the mappings.
        image_path: The path of the temporary images storing the tuple.
    
    Returns:
        text: A string converted from the tuple. 
    '''
    
    if tuple_name == 'name':
        text = pytesseract.image_to_string(img_path, lang = 'deu', config = '--psm 6 ')
        if text[0] == '3':
            text = text.replace('3','S',1)
    elif tuple_name in ['c1','c2','c3','c4','c5','d1','d2','d3','d4','d5']:
        text = pytesseract.image_to_string(img_path, config = '--psm 6 ' + white_list['data'])
        text = text.replace(',','.')
    else:
        text = pytesseract.image_to_string(img_path, lang = 'deu',config = '--psm 6 ')
        
    return text