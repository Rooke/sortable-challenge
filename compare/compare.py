#!/usr/bin/env python
# encoding: utf-8

# Compares two or more solution results, specified in ./entries.json

import json, re, collections, codecs, sys, os, subprocess, resource
from operator import itemgetter
from pprint import pprint

# Abuse some global state:
run_outputs = {}
results = {}

def compare_result(name, compare_to, out):
    cum_missing = 0
    cum_diff = 0
    cum_common = 0
    
    for line in codecs.open(run_outputs[name], encoding="UTF-8").readlines():
        # try to munge invalid json
        line = re.sub("},$", "}", line)
                
        line_json = ""
        try:
            line_json = json.loads(line)
        except ValueError:
            print line
            pass
        if "product_name" not in line_json:
            continue

        product = line_json["product_name"]
        if product in compare_to:
            data1 = compare_to[product]
            newlist1 = sorted(data1, key=itemgetter('title')) 
            
            data2 = line_json["listings"]
            newlist2 = sorted(data2, key=itemgetter('title'))
            
            inter = [x for x in data2 if x in data1]
            diff1 = [x for x in data1 if x not in inter]
            diff2 = [x for x in data2 if x not in inter]

            cum_common += len(inter)
            
            if len(diff1) > 0 or len(diff2) > 0:
                pprint(product, stream=out)
            if len(diff1) > 0:
                out.write("Original had: ")
                pprint(diff1, stream=out)
                cum_missing += len(diff1)
            if len(diff2) > 0:
                pprint(name + " had: ", stream=out)
                pprint(diff2, stream=out)
                cum_diff += len(diff2)

    results[name]["miss"] = cum_missing
    results[name]["diff"] = cum_diff
    results[name]["common"] = cum_common

def run_all_challenges():
    
    file_json = json.loads(open("./entries.json").read())
    for run in file_json:

        orig_dir = os.getcwd()
        
        if "working_dir" in run:
            os.chdir(run["working_dir"])
            
        cmd = []
        cmd.append(run["command"])
        cmd.extend(run["command_args"])
            
        print "Running '" + run["name"] + "'..."
        
        usage_start = resource.getrusage(resource.RUSAGE_CHILDREN)
        subprocess.call(cmd, stdout=open(os.devnull, 'w'), stderr=subprocess.STDOUT)
        usage_end = resource.getrusage(resource.RUSAGE_CHILDREN)
        
        cpu_time = usage_end.ru_utime - usage_start.ru_utime
        memory_use = (usage_end.ru_maxrss - usage_start.ru_maxrss) / 1024.
        
        os.chdir(orig_dir)
        
        results[run["name"]] = {}
        results[run["name"]]["cpu_time"] = cpu_time
        results[run["name"]]["memory_use"] = memory_use
        
        run_outputs[run["name"]] = run["result"]

def main():

    run_all_challenges()
    
    with open('verbose.txt', 'wt') as out:

        # Hack: hardcode the 'compare-to' set
        compare_to = {}
        for line in codecs.open(run_outputs["cpp"], encoding="UTF-8").readlines():
            line_json = json.loads(line)
            
            if "listings" in line_json:
                compare_to[line_json["product_name"]] = line_json["listings"]

        for name in run_outputs:
            compare_result(name, compare_to, out)

    fmt = '{0:15} {1:>8} {2:>11} {3:>6} {4:>11} {5:>8}'
    print fmt.format("Name", "CPU (s)", "Memory (MB)", "diff", "in common", "missed")
    for result in results:
        cpu = format(results[result]["cpu_time"], '.2f')
        mem = format(results[result]["memory_use"], '.2f')
        diff = results[result]["diff"]
        com = results[result]["common"]
        miss = results[result]["miss"]
        print fmt.format(result, cpu, mem, diff, com, miss)
            
main()
