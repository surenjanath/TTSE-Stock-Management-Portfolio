from bs4 import BeautifulSoup as bs
import pandas as pd
import re
import js2py
import requests
import base64

def get_variable(encoded_script):

    decoded_script = base64.b64decode(encoded_script).decode('latin-1')

    js_code = decoded_script.replace('document.cookie','COOKIE').replace("location.reload();","")
    # print('[*] print : ', js_code)
    py_code = js2py.eval_js(js_code)
    result = py_code
    # print('[*] Cookie Code : ', result)
    return result

def get_TTSE_Auth(HEADER):

    # HEADER = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'

    URL = f'https://www.stockex.co.tt/manage-stock/rfhl/'

    headers = {
        'Authority':'www.stockex.co.tt',
        'Method':'GET',
        'Scheme':'https',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9,de;q=0.8',
        'Cache-Control':'no-cache',
        'Cookie':"""sucuri_cloudproxy_uuid_2bf554b18=d8450e5c0a1eb7b610118d5c1a1f5305""".strip(),
        'Pragma':'no-cache',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'cross-site',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent' : HEADER,
    }

    response = requests.get(URL, headers =headers)

    # get_variable(str(response.text))
    soup = bs(response.content, 'lxml')
    scpt = soup.find('script')
    string_of_characters = scpt.text.split('S=')[1].split(';')[0]
    string_of_characters = string_of_characters

    # print(string_of_characters)
    # print('*'*50)
    try:
        decodedCode = get_variable(str(string_of_characters)).split(";")[0]
    except Exception as e:
        print(f'[*] Error : {e}')
    # print('[*] Decoded Security Code : ', decodedCode)
    # print('*'*50)
                                                        #  sucuri_cloudproxy_uuid_39a6883fc=9f489ca8bd4da156a5bbe93c14eeac82
    response = requests.get(URL, headers = {'Cookie':f"""{decodedCode};""".strip(),'User-Agent':HEADER})
    if 'REPUBLIC' in str(response.content):
        return {"Auth": decodedCode}
    else:
        if 'redirected' in str(response.content):
            soup = bs(response.content, 'lxml')
            scpt = soup.find('script')
            coded = scpt.text.split('S=')[1].split(';')[0]
            decoded = base64.b64decode(coded).decode('latin-1')
            js_code = decoded.replace('\n','').replace("location.reload();","").replace("document.cookie","DecodedCode")
            py_code = js2py.eval_js(js_code)
            decodedCode = py_code.split(";")[0]

            response = requests.get(URL, headers = {'Cookie':f"""{decodedCode};""".strip(),'User-Agent':HEADER})

            if 'REPUBLIC' in str(response.content):
                print('Code Generated : ', decodedCode)
                return {"Auth": decodedCode}

    return {"Auth":'Failed'}




def fetchTTSE_DATA(session, TTSE_SYMBOL, TYPE, HEADER_MODEL):
    latest_entry = HEADER_MODEL.objects.latest('date_created')
    scraper_header = latest_entry.__dict__
    TTSE_SYMBOL = str(TTSE_SYMBOL).upper()
    UserAgent = scraper_header['header']

    AUTH_COOKIE = scraper_header['cookie_code']
    headers = {
        'Authority':'www.stockex.co.tt',
        'Method':'GET',
        'Scheme':'https',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Encoding':'gzip, deflate, br',
        'Accept-Language':'en-US,en;q=0.9,de;q=0.8',
        'Cache-Control':'no-cache',
        'Cookie':f"""{AUTH_COOKIE};""".strip(),
        'Pragma':'no-cache',
        'Sec-Ch-Ua-Mobile':'?0',
        'Sec-Ch-Ua-Platform':'"Windows"',
        'Sec-Fetch-Dest':'document',
        'Sec-Fetch-Mode':'navigate',
        'Sec-Fetch-Site':'cross-site',
        'Sec-Fetch-User':'?1',
        'Upgrade-Insecure-Requests':'1',
        'User-Agent' : UserAgent,
    }
    URL = f'https://www.stockex.co.tt/manage-stock/{TTSE_SYMBOL}/'

    response = requests.get(URL, headers = headers)

    if ('redirect' in str(response.text)) and (TTSE_SYMBOL not in str(response.text)):
        latest_entry.status = False
        latest_entry.save()


        latest_entry = HEADER_MODEL.objects.latest('date_created')
        scraper_header = latest_entry.__dict__

        UserAgent = scraper_header['header']
        AUTH_COOKIE = scraper_header['cookie_code']

        headers = {
            'Authority':'www.stockex.co.tt',
            'Method':'GET',
            'Scheme':'https',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Encoding':'gzip, deflate, br',
            'Accept-Language':'en-US,en;q=0.9,de;q=0.8',
            'Cache-Control':'no-cache',
            'Cookie':f"""{AUTH_COOKIE};""".strip(),
            'Pragma':'no-cache',
            'Sec-Ch-Ua-Mobile':'?0',
            'Sec-Ch-Ua-Platform':'"Windows"',
            'Sec-Fetch-Dest':'document',
            'Sec-Fetch-Mode':'navigate',
            'Sec-Fetch-Site':'cross-site',
            'Sec-Fetch-User':'?1',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent' : UserAgent,
        }

        response = requests.get(URL, headers=headers)
        if 'redirect' in str(response.text):

            return {
                'status': 'error',
                'message': 'Web scraping failed twice.',
            }

    return {
        'status': 'success',
        'body' : response.content,
        'message': 'Web scraping succeeded on the second attempt.',
    }


