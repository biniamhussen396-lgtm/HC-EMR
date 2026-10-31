#!/bin/bash
for t in mindraybc dxh dxc humastar advia genexpert; do
    code=$(curl -s -o /dev/null -w '%{http_code}' "http://localhost:8052/openelis/AnalyzerResults.do?type=$t")
    echo "$t: $code"
done
