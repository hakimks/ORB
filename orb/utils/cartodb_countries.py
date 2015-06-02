'''
 Script to update user map on CartoDB
 
 For full instructions, see the documentation at 
 https://oppiamobile.readthedocs.org/en/latest/
'''

import time 
import urllib
import json 
import argparse, hashlib, subprocess


from orb.models import Tag,Category,Resource


def run(cartodb_account, cartodb_key): 
    
    cartodb_table = "orbcountries" 
    
    category = Category.objects.get(slug='geography')
    countries = Tag.objects.filter(category=category,resourcetag__resource__status=Resource.APPROVED).distinct()
    
    sql = "UPDATE %s SET display=False" % (cartodb_table)
    url = "http://%s.cartodb.com/api/v2/sql?q=%s&api_key=%s" % (cartodb_account,sql,cartodb_key)
    u = urllib.urlopen(url)
    data = u.read() 
    dataJSON = json.loads(data)
    print dataJSON
    
    for c in countries:
        sql = "UPDATE %s SET display=True WHERE name = '%s'" % (cartodb_table,c.name)
        url = "http://%s.cartodb.com/api/v2/sql?q=%s&api_key=%s" % (cartodb_account,sql,cartodb_key)
        u = urllib.urlopen(url)
        data = u.read() 
        dataJSON = json.loads(data)
        print c.name
        print dataJSON
        time.sleep(1)
    
 
if __name__ == "__main__":
    import django
    django.setup()
    parser = argparse.ArgumentParser()
    parser.add_argument("cartodb_account", help="CartoDB Account Name")
    parser.add_argument("cartodb_key", help="CartoDB API Key")
    args = parser.parse_args()
    run(args.cartodb_account, args.cartodb_key)  
    
    
    
    