from django.conf import settings
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
import urllib
from urllib import request, parse
import csv
import os
import json
import base64
import http.client
import time
import sys
import shutil
import logging


from .models import Greeting

# Create your views here.
def index(request):
    # return HttpResponse('Hello from Python!')
    return render(request, "index.html")

def buildKit(request, kitinput):
    kitkey = kitinput

    url = "http://www84.pair.com/clevtool/shopify-kits/%s.csv" % kitkey
    with urllib.request.urlopen(url) as f, open('%s.csv' % kitkey, 'wb') as outfile:
        shutil.copyfileobj(f, outfile)

    filename = '%s.csv' % (kitkey)
    message = 'retrieved %s' % (filename)
    logging.debug(message)

    ### Parse CSV and Generate Order Line Item Array

    r1 = 'Variant ID'
    r2 = 'Metafield: ' + kitkey + ' [integer]'
    r3 = 'Variant Metafield: ' + kitkey + ' [integer]'
    r4 = 'Metafield: ' + kitkey + ' [string]'
    r5 = 'Variant SKU'
    r6 = 'Option1 Value'

    lineitems = []

    with open(filename, newline='') as csvfile:
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
                logging.debug(output)
                time.sleep(.25)

    draftorderoutput = {
        'draft_order':
        {
            'tags': '%s Auto Created' % (kitkey),
            'line_items':lineitems
        }
    }

    json_order = json.dumps(draftorderoutput)

    ### Connect to Shopify and Make Draft Order

    host = 'cleaveland-aircraft-tool-3.myshopify.com'
    endpoint = '/admin/api/2020-01/draft_orders.json'
    headers = {
        'X-Shopify-Access-Token': '6fc2d89e55f911aa86673ed6d4a12b7f',
        'Content-Type': 'application/json',
    }

    conn = http.client.HTTPSConnection(host)
    conn.request('POST', endpoint, json_order, headers)
    r = conn.getresponse()
    logging.debug(r.headers)
    loc = r.headers["Location"]

    conn.close()

    ### remove local CSV file
    os.remove(filename)

    ###
    # return render(request, "build.html",
    # {
    #     'location': loc,
    #     'kitkey': kitkey,
    # }
    # )

    ### Redirect to the newly created draft order
    return redirect(loc)

def selectKit(request):
    return render(request, "select.html")

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})
