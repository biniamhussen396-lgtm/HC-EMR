#!/usr/bin/env python
"""
OpenELIS Analyzer TCP/IP Bridge
Listens for ASTM protocol data from Mindray BC 5150 (or similar)
and forwards results to OpenELIS via HTTP POST.

Usage: python analyzer_bridge.py [listen_port] [openelis_url]
"""

import socket
import sys
import json
import time
import urllib2
import re

LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5100
OPENELIS_URL = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:8052/openelis/addAnalyzerData"
MACHINE_NAME = "mindray bc 5150"

def parse_astm_frame(data):
    """Parse ASTM protocol frame and extract patient results."""
    results = []
    
    # ASTM records are separated by CR (\r) and framed with ETX (\x03) or EOT (\x04)
    # Split by carriage return
    records = data.split('\r')
    
    sample_id = None
    test_results = []
    
    for record in records:
        record = record.strip('\x02\x03\x04\x05\x15\x06')
        if not record:
            continue
            
        # Determine record type from first character
        if len(record) < 2:
            continue
            
        record_type = record[0]
        fields = record.split('|')
        
        # P (Patient) record - contains sample/order info
        if record_type == 'P' or record_type == 'O':
            # Field 2 or 3 contains the sample/accession number
            if len(fields) > 2:
                sample_id = fields[2].split('^')[0].strip()
            elif len(fields) > 1:
                sample_id = fields[1].split('^')[0].strip()
        
        # R (Result) record - contains test results
        elif record_type == 'R':
            if len(fields) >= 3:
                # Field 2: test name (may have ^ separators)
                test_name_raw = fields[1] if len(fields) > 1 else ''
                test_name = test_name_raw.split('^')[0].strip()
                
                # Field 3: result value
                result_value = fields[2].split('^')[0].strip() if len(fields) > 2 else ''
                
                # Field 4: units (optional)
                units = ''
                if len(fields) > 3:
                    units = fields[3].split('^')[0].strip()
                
                # Field 6: result status (C=final, P=preliminary)
                status = fields[5].split('^')[0].strip() if len(fields) > 5 else 'C'
                
                if test_name and result_value:
                    test_results.append({
                        'parameterName': test_name.upper(),
                        'result': result_value,
                        'units': units
                    })
        
        # Q (Query) record - may contain sample info
        elif record_type == 'Q':
            if len(fields) > 2:
                sample_id = fields[2].split('^')[0].strip()
    
    # Build results list
    if sample_id and test_results:
        for tr in test_results:
            results.append({
                'machineName': MACHINE_NAME,
                'sampleId': sample_id,
                'parameterName': tr['parameterName'],
                'result': tr['result'],
                'units': tr['units'],
                'completeDate': time.strftime('%y-%m-%d %H:%M')
            })
    
    return results


def parse_simple_result(data):
    """
    Parse simple CSV/TSV format: sampleId,testName,result,units
    Example: SAMPLE001,WBC,7.5,10^3/uL
    """
    results = []
    lines = data.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split(',')
        if len(parts) >= 3:
            sample_id = parts[0].strip()
            test_name = parts[1].strip().upper()
            result_value = parts[2].strip()
            units = parts[3].strip() if len(parts) > 3 else ''
            
            results.append({
                'machineName': MACHINE_NAME,
                'sampleId': sample_id,
                'parameterName': test_name,
                'result': result_value,
                'units': units,
                'completeDate': time.strftime('%y-%m-%d %H:%M')
            })
    
    return results


def post_to_openelis(results):
    """POST results to OpenELIS HTTP endpoint."""
    for result in results:
        try:
            json_data = json.dumps(result)
            req = urllib2.Request(
                OPENELIS_URL,
                data=json_data,
                headers={'Content-Type': 'application/json'}
            )
            response = urllib2.urlopen(req, timeout=10)
            print "  [OK] %s: %s = %s %s -> HTTP %d" % (
                result['sampleId'], result['parameterName'],
                result['result'], result['units'], response.getcode()
            )
        except Exception as e:
            print "  [ERROR] %s: %s" % (result['parameterName'], str(e))


def main():
    print "=== OpenELIS Analyzer Bridge ==="
    print "Machine: %s" % MACHINE_NAME
    print "Listening on port: %d" % LISTEN_PORT
    print "OpenELIS endpoint: %s" % OPENELIS_URL
    print "Waiting for analyzer data..."
    print ""

    # Create TCP socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', LISTEN_PORT))
    server.listen(1)
    
    while True:
        try:
            client, addr = server.accept()
            print "Connection from %s:%d" % addr
            
            # Receive data
            raw_data = ''
            client.settimeout(30)
            while True:
                try:
                    chunk = client.recv(4096)
                    if not chunk:
                        break
                    raw_data += chunk
                    # Check for end of transmission
                    if '\x04' in raw_data or '\x03' in raw_data[-1:]:
                        break
                except socket.timeout:
                    break
            
            client.close()
            
            if not raw_data:
                print "  No data received"
                continue
            
            print "  Received %d bytes" % len(raw_data)
            
            # Try ASTM parsing first
            results = parse_astm_frame(raw_data)
            
            # If no ASTM results, try simple CSV format
            if not results:
                results = parse_simple_result(raw_data)
            
            if results:
                print "  Parsed %d result(s), sending to OpenELIS..." % len(results)
                post_to_openelis(results)
            else:
                print "  Could not parse results from data"
                print "  Raw data (first 200 chars): %s" % raw_data[:200]
            
            print "Waiting for analyzer data..."
            
        except KeyboardInterrupt:
            print "\nShutting down..."
            break
        except Exception as e:
            print "Error: %s" % str(e)
    
    server.close()


if __name__ == '__main__':
    main()
