import csv
import sys

ref_service = env['reference.data.service']
ProductProduct = env['product.product'].with_context({'active_test': False})

existing_uuids = set(ProductProduct.search([]).mapped('uuid'))
print('Already existing UUIDs:', len(existing_uuids))

created = 0
for enc in ['utf-8-sig', 'utf-16', 'utf-8', 'latin-1']:
    try:
        with open('/tmp/missing_concepts.tsv', 'r', encoding=enc) as f:
            lines = f.readlines()
        print('Opened file using encoding:', enc, 'lines:', len(lines))
        break
    except Exception:
        continue

for line in lines:
    parts = line.strip().split('\t')
    if len(parts) < 3:
        continue
    uuid, name, cls = parts[0].strip(), parts[1].strip(), parts[2].strip()
    if uuid in existing_uuids or not uuid:
        continue
    
    cat = 'Test'
    if cls in ['Panel', 'LabSet']:
        cat = 'Panel'
    elif cls == 'Radiology':
        cat = 'Radiology'
        
    try:
        ref_service.create_or_update_ref_data({
            'uuid': uuid,
            'name': name,
            'is_active': True,
            'product_category': cat
        }, cat)
        existing_uuids.add(uuid)
        created += 1
        if created % 100 == 0:
            env.cr.commit()
            print('Created', created, 'products...')
    except Exception as e:
        print('Error creating', name, uuid, ':', e)

env.cr.commit()
print('DONE! Total new products created:', created)
