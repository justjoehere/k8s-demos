#!/usr/bin/env python
import sys
import os
import rasterio
from rio_cloudmask.equations import cloudmask
from subprocess import check_output

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("mabl-k8s-demo-fb-key.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://load-testing-160018.firebaseio.com/'
})

DATA_IN_PATH = '/tmp/raw_data_in/'
DATA_OUT_PATH = '/tmp/raw_data_out/'

DATA_SIZE = 0


def increment_value(current_value):
    return current_value + 1 if current_value else 1


def increment_datasize(current_value):
    global DATA_SIZE
    return current_value + DATA_SIZE if current_value else DATA_SIZE


def update_tile_list(tile_id):
    tiles_ref = db.reference('tiles')
    try:
        tiles_ref.push(tile_id)
        print 'Transaction completed'
    except db.TransactionError:
        print 'Transaction failed to commit'


def update_firebase_counts():
    proc_cnt_ref = db.reference('statistics/processedCount')
    try:
        proc_cnt_ref.transaction(increment_value)
        print 'Transaction completed'
    except db.TransactionError:
        print 'Transaction failed to commit'


def update_firebase_sizes(size_bytes):
    global DATA_SIZE
    DATA_SIZE = size_bytes

    proc_cnt_ref = db.reference('statistics/processedBytes')
    try:
        proc_cnt_ref.transaction(increment_datasize)
        print 'Transaction completed'
    except db.TransactionError:
        print 'Transaction failed to commit'


def copy_tiles_to_local(tile_gs_dir):
    print "Syncing files from %s" % tile_gs_dir
    cmd_parts = ['gsutil', '-q', 'rsync', tile_gs_dir, DATA_IN_PATH]
    check_output(cmd_parts)
    update_firebase_sizes(get_dir_size(DATA_IN_PATH))


# def convert_to_toa(src_path, src_mtl, dst_path):
#     creation_options = {}
#     dst_dtype = 'uint8'
#     rescale_factor = 215
#     processes = 1
#     pixel_sunangle = True
#
#     reflectance.calculate_landsat_reflectance([src_path], src_mtl,
#                                               dst_path, rescale_factor,
#                                               creation_options, [4, 3, 2],
#                                               dst_dtype, processes,
#                                               pixel_sunangle)
#

def doProcessing(tile_gs_dir):
    tile_id = tile_gs_dir[::-1].split('/', 2)[0][::-1]

    print "processing tile from [%s]" % tile_id
    data_root = DATA_IN_PATH

    update_tile_list(tile_id)
    copy_tiles_to_local(tile_gs_dir)
    update_firebase_counts()


    print "Analyzing images"

    # for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]:
    #     try:
    #         src_path = '%s/%s_B%s.TIF' % (data_root, tile_id, i)
    #         src_mtl_path = '%s/%s_MTL.txt' % (data_root, tile_id)
    #         dst_path = src_path.replace('.TIF', '_toa.TIF')
    #
    #         print 'Converting [%s] with [%s] to [%s]' % (src_path, src_mtl_path, dst_path)
    #         convert_to_toa(src_path, src_mtl_path, dst_path)
    #     except Exception:
    #         continue

    pref = '%s/%s_' % (data_root, tile_id)

    try:
        blue = rasterio.open(pref + "B2_toa.TIF").read(1)
        green = rasterio.open(pref + "B3_toa.TIF").read(1)
        red = rasterio.open(pref + "B4_toa.TIF").read(1)
        nir = rasterio.open(pref + "B5_toa.TIF").read(1)
        swir1 = rasterio.open(pref + "B6_toa.TIF").read(1)
        swir2 = rasterio.open(pref + "B7_toa.TIF").read(1)
        cirrus = rasterio.open(pref + "B9_toa.TIF").read(1)
        tirs1 = rasterio.open(pref + "B10_toa.TIF").read(1)

        with rasterio.open(pref + "B2_toa.TIF") as src1:
            profile = src1.profile

        profile['dtype'] = 'uint8'

        clouds, shadows = cloudmask(
            blue, green, red, nir, swir1, swir2, cirrus, tirs1)

        with rasterio.open('pcl.TIF', 'w', **profile) as dst:
            dst.write((~(clouds | shadows) * 255).astype('uint8'), 1)

        death = 1/0
    except:
        pass

def get_dir_size(start_path='.'):
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(start_path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            total_size += os.path.getsize(fp)
    return total_size


if __name__ == "__main__":
    tile_id = sys.argv[1]
    doProcessing(tile_id)
