from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import js2py
import requests
import base64

def get_variable(encoded_script):

    decoded_script = base64.b64decode(encoded_script).decode('latin-1')
    js_code = decoded_script.replace('document.cookie','COOKIE').replace("location.reload();","")
    py_code = js2py.eval_js(js_code)
    result = py_code
    return result


def fetchTTSE_DATA(session, headers, TTSE_SYMBOL, TYPE):

    URL = f'https://www.stockex.co.tt/manage-{TYPE}/{TTSE_SYMBOL}/'
    response = requests.get(URL, headers =headers)

    response = requests.get(URL, headers =headers)

    # get_variable(str(response.text))
    soup = bs(response.content, 'lxml')
    scpt = soup.find('script')
    string_of_characters = scpt.text.split('S=')[1].split(';')[0]
    string_of_characters = string_of_characters

    # print(string_of_characters)
    print('*'*50)
    try:
        decodedCode = get_variable(str(string_of_characters)).split(";")[0]
    except Exception as e:
        print(f'[*] Error : {e}')
    print('[*] Decoded Security Code : ', decodedCode)
    print('*'*50)
                                                        #  sucuri_cloudproxy_uuid_39a6883fc=9f489ca8bd4da156a5bbe93c14eeac82
    response = requests.get(URL, headers = {'Cookie':f"""{decodedCode};""".strip(),'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})

    if 'redirected' in str(response.content):
        soup = bs(response.content, 'lxml')

        scpt = soup.find('script')
        coded = scpt.text.split('S=')[1].split(';')[0]
        decoded = base64.b64decode(coded).decode('latin-1')

        js_code = decoded.replace('\n','').replace("location.reload();","").replace("document.cookie","DecodedCode")
        py_code = js2py.eval_js(js_code)
        decodedCode = py_code.split(";")[0]

        response = requests.get(URL, headers = {'Cookie':f"""{decodedCode};""".strip(),'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'})
        print(response.text)
        return "good"
    return "not good"


