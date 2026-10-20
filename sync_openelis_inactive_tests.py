import urllib.request
import json
import mysql.connector
import uuid
import time
import sys

def sync():
    try:
        # 1. Fetch inactive tests from OpenELIS JSP endpoint
        req = urllib.request.Request('http://localhost:8186/openelis/pages/test/inactiveTests.jsp')
        with urllib.request.urlopen(req, timeout=5) as resp:
            inactive_map = json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f"Error fetching from OpenELIS inactiveTests.jsp: {e}")
        return

    inactive_clean = {k.strip().lower() for k in inactive_map.keys()}

    try:
        # 2. Connect to OpenMRS MySQL
        my_conn = mysql.connector.connect(
            host='127.0.0.1',
            port=3206,
            database='openmrs',
            user='openmrs-user',
            password='password'
        )
        my_cur = my_conn.cursor(dictionary=True)

        matched_cids = set()

        # For each inactive test, find concept and ensure $inactive exists
        for clean_name in inactive_clean:
            my_cur.execute("""
                SELECT c.concept_id 
                FROM concept c 
                JOIN concept_name cn ON c.concept_id = cn.concept_id 
                WHERE LOWER(TRIM(cn.name)) = %s AND cn.voided = 0
                LIMIT 1
            """, (clean_name,))
            res = my_cur.fetchone()
            if res:
                cid = res['concept_id']
                matched_cids.add(cid)
                my_cur.execute("SELECT concept_name_id, voided FROM concept_name WHERE concept_id = %s AND name = '$inactive'", (cid,))
                existing = my_cur.fetchone()
                if not existing:
                    u = str(uuid.uuid4())
                    my_cur.execute("""
                        INSERT INTO concept_name (concept_id, name, locale, creator, date_created, voided, uuid)
                        VALUES (%s, '$inactive', 'en', 1, NOW(), 0, %s)
                    """, (cid, u))
                    my_conn.commit()
                    print(f"Added $inactive for concept {cid} ({clean_name})")
                elif existing['voided'] == 1:
                    my_cur.execute("UPDATE concept_name SET voided = 0 WHERE concept_id = %s AND name = '$inactive'", (cid,))
                    my_conn.commit()
                    print(f"Un-voided $inactive for concept {cid} ({clean_name})")

        # Void $inactive for any concept that is currently active in OpenELIS
        my_cur.execute("""
            SELECT cn.concept_name_id, cn.concept_id, (
                SELECT name FROM concept_name cn2 
                WHERE cn2.concept_id = cn.concept_id AND cn2.concept_name_type = 'FULLY_SPECIFIED' AND cn2.voided = 0 LIMIT 1
            ) AS full_name
            FROM concept_name cn
            WHERE cn.name = '$inactive' AND cn.voided = 0
        """)
        active_inactives = my_cur.fetchall()
        for row in active_inactives:
            cid = row['concept_id']
            if cid not in matched_cids:
                # This concept is not currently inactive in OpenELIS, so void $inactive
                my_cur.execute("UPDATE concept_name SET voided = 1, void_reason = 'Reactivated in OpenELIS' WHERE concept_name_id = %s", (row['concept_name_id'],))
                my_conn.commit()
                print(f"Voided $inactive for reactivated concept {cid} ({row['full_name']})")

        my_cur.close()
        my_conn.close()
    except Exception as e:
        print(f"Error syncing with OpenMRS MySQL: {e}")

if __name__ == '__main__':
    if '--watch' in sys.argv:
        print("Starting inactive tests sync daemon (every 10s)...")
        while True:
            sync()
            time.sleep(10)
    else:
        sync()
