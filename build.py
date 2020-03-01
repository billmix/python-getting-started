from ftplib import FTP
from urllib import request, parse
import csv
import os
import json
import base64
import http.client
import time
import sys

def grabFile(request, kitinput):
    kitkey = kitinput
    ftp = FTP('clevtool.pairserver.com')
    ftp.login('clevtool_shopify_excelify', 'AHGhAp,Uis6K%DsudHV')
    filename = '%s.csv' % (kitkey)
    message = 'retrieved %s' % (filename)
    print(message)

    localfile = open(filename, 'wb')
    ftp.retrbinary('RETR ' + filename, localfile.write, 1024)

    ftp.quit

    localfile.close()

    readCSV(filename, kitkey)


def readCSV(kitfile, kitkey):
    r1 = 'Variant ID'
    r2 = 'Metafield: ' + kitkey + ' [integer]'
    r3 = 'Variant Metafield: ' + kitkey + ' [integer]'
    r4 = 'Metafield: ' + kitkey + ' [string]'
    r5 = 'Variant SKU'
    r6 = 'Option1 Value'

    lineitems = []

    with open(kitfile) as csvfile:
        reader = csv.DictReader(csvfile)
        for index, row in enumerate(reader):
            if row[r2] == '' and row[r3] == '' and row[r4] == '':
                continue
            elif row[r2] is None or row[r3] is None or row[r4] is None:
                continue
            elif row[r2] != '' and row[r2] != 0:
                qty = int(row[r2])
            elif row[r3] != ''  and row[r3] != 0:
                qty = int(row[r3])
            elif row[r4] != ''  and row[r3] != 0:
                qty = int(row[r4])
            if qty != 0:
                lineitems.append({
                 'variant_id': int(row[r1]),
                 'quantity': qty
                })
                output = row[r6] + ' ' + row[r5] + ' ' + str(qty)
                print(output)
                time.sleep(.25)


    cleanUp(kitfile)

    createDraftOrder(lineitems, kitkey)

def createDraftOrder(lineitems, kitkey):
    print('Opening connection with Shopify')
    draftorderoutput = {
            'draft_order':
            {
                'tags': '%s Auto Created' % (kitkey),
                'line_items':lineitems
            }
        }

    json_order = json.dumps(draftorderoutput)

    host = 'cleaveland-aircraft-tool-3.myshopify.com'
    endpoint = '/admin/api/2020-01/draft_orders.json'

    headers = {
        'X-Shopify-Access-Token': '6fc2d89e55f911aa86673ed6d4a12b7f',
        'Content-Type': 'application/json',
    }

    conn = http.client.HTTPSConnection(host)
    conn.request('POST', endpoint, json_order, headers)
    response = conn.getresponse()

    conn.close()

def cleanUp(kitfile):
    os.remove(kitfile)
