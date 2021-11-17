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

import os
import psycopg2

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
        
        for factor in range(2, number >> 1):
            if number % factor == 0:
                return False
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
        self.my_host = my_host
        self.conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port)

    def _get_record(self, index):
        '''
        '''
        cursor = self.conn.cursor()
        cursor.execute("SELECT VALUE FROM WORK WHERE ID = %d;" % index)
        rows = cursor.fetchall()
        if len(rows) == 1:
            return rows[0][0]
        raise Exception("Could not retrieve record from database")

    def _save_result(self, index, result):
        '''
        '''
        cursor = self.conn.cursor()
        cursor.execute("UPDATE WORK SET NEARPRIME = %d, PROCESSEDBY = '%s' WHERE ID = %d;" % (result, self.my_host, index))
        self.conn.commit()

    def process(self, index):
        '''
        '''


def main():
    '''
    The main function runs only if this module is directly executed (i.e. not
    imported elsewhere as a library).
    '''
    database = os.getenv('DDW_DATABASE', 'demo-db')
    user     = os.getenv('DDW_USER',     'demo')
    password = os.getenv('DDW_PASSWORD', 'demopass')
    host     = os.getenv('DDW_HOST',     '127.0.0.1')
    port     = os.getenv('DDW_PORT',     '5432')
    my_host  = os.getenv('HOSTNAME',     'unknown')

    np = NearestPrime()
    db = Db(database, user, password, host, port, my_host)

    setup = Setup(database, user, password, host, port)
    setup.drop_table()
    setup.create_table()
    setup.fill_table(1000)
    setup.close()


if __name__ == '__main__':
    # Run as the main module, not imported
    main()    