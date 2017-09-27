#!/usr/bin/env python
from subprocess import check_output
import uuid
from tempfile import mkstemp
import os
import sys

def loadTileIds():
    curr_dir = os.path.dirname(os.path.realpath(__file__))
    filename = os.path.join(curr_dir, "gs_paths.txt")
    
    with open(filename) as f:
        content = f.readlines()
        content = [x.strip() for x in content]

    print "Loaded %s ids" % len(content)
    return content

def runJob(image_tag, tile_gs_dir):

    print "Launching jobs for %s" % tile_gs_dir
    configJson = makeConfigJson(image_tag, tile_gs_dir)
    fd, config_path = mkstemp()
    os.close(fd)

    with open(config_path, "w") as text_file:
        text_file.write(configJson)

    cmd_parts = ['kubectl', 'create', '-f', config_path, '--validate=false']
    check_output(cmd_parts)

def makeConfigJson(image_tag, tile_gs_dir):
    jobName = str(uuid.uuid1())

    # TODO switch to named interpolation values
    config = """{
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": "%s",
            "namespace": "default"
        },
        "spec": {
            "template": {
                "spec": {
                    "restartPolicy": "Never",
                    "containers": [{
                        "name": "%s",
                        "image": "%s",
                        "args": [
                            "%s"
                        ],
                        "imagePullPolicy": "Never",
                        "activeDeadlineSeconds": 1800,
                        "resources": {
                            "requests": {
                                "cpu": "500m",
                                "memory": "512Mi"
                            },
                            "limits": {
                                "cpu": "500m",
                                "memory": "512Mi"
                            }
                        }
                    }]
                }
            }
        }
    }""" % (jobName,jobName,image_tag, tile_gs_dir)
    return config

if __name__ == "__main__":

    image_tag = sys.argv[1]

    n = 0
    limit = 10000

    print "Submitting %s instances of job with image tag [%s]" % (limit, image_tag)

    # TODO pass in limit arg
    for tile_id in loadTileIds():
        n += 1
        runJob(image_tag, tile_id)

        if n >= limit:
            exit("Limit reached")

