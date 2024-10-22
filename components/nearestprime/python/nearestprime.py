#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License
#

import sys
import os
import psycopg2
import falcon
import json
import math
from time import time

class NearestPrime(object):
    '''
    '''
    def __init__(self):
        pass

    def is_prime(self, number):
        '''
        '''
        if number < 3:
            return True
        
        if number % 2 == 0:
            return False
        
        factor = 3
        limit  = math.sqrt(number)
        while factor <= limit:
            if number % factor == 0:
                return False
            factor += 2
        return True

    def nearest(self, number):
        '''
        '''
        if self.is_prime(number):
            return number

        for delta in range(1, number):
            if self.is_prime(number + delta):
                return number + delta
            if self.is_prime(number - delta):
                return number - delta

        raise Exception("We shouldn't have arrived here")


class Db(object):
    '''
    '''
    def __init__(self, database, user, password, host, port, my_host):
        '''
        '''
        self.database = database
        self.user     = user
        self.password = password
        self.host     = host
        self.port     = port
        self.my_host  = my_host
        self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    def check_connection(self):
        if self.conn.closed:
            print("Re-establishing database connection...", file=sys.stderr)
            self.conn = psycopg2.connect(database=self.database, user=self.user, password=self.password, host=self.host, port=self.port)

    def get_record(self, index):
        '''
        '''
        self.check_connection()
        cursor = self.conn.cursor()
        cursor.execute("SELECT VALUE FROM WORK WHERE ID = %d;" % index)
        rows = cursor.fetchall()
        cursor.close()
        if len(rows) == 1:
            return rows[0][0]
        raise Exception("Could not retrieve record from database")

    def save_result(self, index, result, fetch_time, compute_time):
        '''
        '''
        self.check_connection()
        cursor = self.conn.cursor()
        cursor.execute("UPDATE WORK SET NEARPRIME = %d, PROCESSEDBY = '%s', fetchtime=%.3f, computetime=%.3f WHERE ID = %d;" % (result, self.my_host, fetch_time, compute_time, index))
        self.conn.commit()
        cursor.close()


class Endpoint(object):
    '''
    '''
    def __init__(self, np, db, my_host):
        self.np      = np
        self.db      = db
        self.my_host = my_host

    def on_get(self, req, resp):
        '''
        '''
        tries = 2
        while tries > 0:
            try:
                tries -= 1
                index = req.get_param_as_int('id')
                time_0 = time()
                in_value = self.db.get_record(index)
                time_1 = time()
                out_value = self.np.nearest(in_value)
                time_2 = time()

                fetch_time = time_1 - time_0
                compute_time  = time_2 - time_1

                self.db.save_result(index, out_value, fetch_time, compute_time)
                time_3 = time()

                store_time = time_3 - time_2
                total_time = time_3 - time_0

                result = {
                    'status'    : 'success',
                    'processor' : self.my_host,
                    'in_value'  : in_value,
                    'out_value' : out_value
                }
                resp.body = json.dumps(result)
                resp.status = falcon.HTTP_200
                tries = 0
                print("OK  - id: %5r in: %9r out: %9r fetch: %1.3f comp: %1.3f sto: %1.3f tot: %1.3f" % \
                      (index, in_value, out_value, fetch_time, compute_time, store_time, total_time), file=sys.stderr)
            except Exception as error:
                print("ERR - %r" % error, file=sys.stderr)
                if tries > 0:
                    print("Retrying transaction...", file=sys.stderr)
                else:
                    result = {
                        'status' : 'error',
                        'error'  : '%r' % error
                    }
                    resp.body = json.dumps(result)
                    resp.status = falcon.HTTP_500


class Health(object):
    '''
    '''
    def __init__(self):
        pass

    def on_get(self, req, resp):
        '''
        '''
        print("LIVENESS PROBE", file=sys.stderr)
        resp.body = "OK"
        resp.status = falcon.HTTP_200


def main(api):
    '''
    The main function runs only if this module is directly executed (i.e. not
    imported elsewhere as a library).
    '''
    database = os.getenv('DDW_DATABASE', 'demo-db')
    user     = os.getenv('DDW_USER',     'demo')
    password = os.getenv('DDW_PASSWORD', 'demopass')
    host     = os.getenv('DDW_HOST',     '127.0.0.1')
    port     = os.getenv('DDW_PORT',     '5432')
    sitename = os.getenv('DDW_SITENAME', None)
    hostname = os.getenv('HOSTNAME',     'unknown')

    small_hostname = ''
    if '-' in hostname:
        small_hostname = hostname[-6:]
    else:
        small_hostname = hostname

    if sitename:
        my_host = "%s (%s)" % (sitename, small_hostname)
    else:
        my_host = hostname

    print(f"Connection Details:\nDatabase: {database}\nUser: {user}\nHost: {host}\nPort: {port}\nMy_Host: {my_host}\n", file=sys.stderr)
    np = NearestPrime()
    db = Db(database, user, password, host, port, my_host)
    endpoint = Endpoint(np, db, my_host)
    api.add_route('/post_work', endpoint)
    api.add_route('/healthz', Health())


#np = NearestPrime()
#for m in range(10000000, 20000000):
#    n = np.nearest(m)
#    print("%7d: %7d" % (m,n))
#exit(0)

api = falcon.API()
main(api)
