from dbfread import DBF
import os
from collections import defaultdict
from dbfread import FieldParser

class MyFieldParser(FieldParser):
    def parseN(self, field, data):
        data = data.strip().strip(b'*\x00')  # Had to strip out the other characters first before \x00, as per super function specs.
        return super(MyFieldParser, self).parseN(field, data)

    def parseD(self, field, data):
        data = data.strip(b'\x00')
        return super(MyFieldParser, self).parseD(field, data)

def original_files(root_folder = 'geography_dbf'):
    files = [f for f in os.listdir(root_folder) if '.dbf' in f]
    division, district, upazila = set(), set(), set()
    under_division, under_district = defaultdict(list), defaultdict(list)
    all_records = []
    for file in files:
        for record in DBF(os.path.join(root_folder,file), parserclass=MyFieldParser):
            all_records.append(record)
            div, dis, upa = record.get('NAME_1', None), record.get('NAME_2', None), record.get('NAME_3', None)
            if div: division.add(div)
            if dis:
                district.add(dis.lower())
                if div and dis not in under_division[div]: under_division[div].append(dis)
            if upa:
                if dis and upa not in under_district[dis]: under_district[dis].append(upa)
                upazila.add(upa)
    return division,district,upazila

def shamnun_get_div(record):
    div = record.get('NAME_1', None)
    if not div: raise Exception('Division not readable')
    div = div.lower().strip()
    return div

def shamnun_get_dist(record):
    dist = record.get('NAME_2', None)
    if not dist: raise Exception('District not readable')
    dist = dist.lower().strip()
    return dist

def shamnun_get_upa(record):
    upa = record.get('NAME_3', None)
    if not upa: raise Exception('Upazila not readable')
    upa = upa.lower().strip()
    return upa

def shammun_dbf_files(root_folder = 'shammun_geography_dbf', division_file='division.dbf',
                      district_file='district.dbf', upazila_file='upazila.dbf'):
    division_file_path = os.path.join(root_folder, division_file)
    district_file_path = os.path.join(root_folder, district_file)
    upazila_file_path = os.path.join(root_folder, upazila_file)

    division, district, upazila = set(), set(), set()
    under_division, under_district = defaultdict(list), defaultdict(list)
    for record in DBF(division_file_path, parserclass=MyFieldParser):
        div = shamnun_get_div(record)
        division.add(div)

    for record in DBF(district_file_path, parserclass=MyFieldParser):
        div = shamnun_get_div(record)
        if div not in division: raise Exception('Incorrect division in district.dbf', div)
        dist = shamnun_get_dist(record)
        district.add(dist)
        under_division[div].append(dist)

    for record in DBF(upazila_file_path, parserclass=MyFieldParser):
        div = shamnun_get_div(record)
        if div not in division: raise Exception('Incorrect division in district.dbf', div)
        dist = shamnun_get_dist(record)
        if dist not in district: raise Exception('Incorrect district in district.dbf', dist)
        upa = shamnun_get_upa(record)
        upazila.add(upa)
        under_district[dist].append(upa)
# shammun_dbf_files()