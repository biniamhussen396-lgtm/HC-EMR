#!/bin/bash
set -e
echo "[1/4] Extracting archive..."
rm -rf /tmp/clinical_fix_deploy
mkdir -p /tmp/clinical_fix_deploy
tar -xzf /tmp/clinical_fix_deploy.tar.gz -C /tmp/clinical_fix_deploy

echo "[2/4] Deploying files to /opt/emr/..."
cp /tmp/clinical_fix_deploy/apps/ui/app/common/util/httpErrorInterceptor.js /opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/app.js /opt/emr/apps/ui/app/clinical/app.js
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/index.html /opt/emr/apps/ui/app/clinical/index.html
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/consultation/views/orders.html /opt/emr/apps/ui/app/clinical/consultation/views/orders.html
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/consultation/controllers/orderController.js /opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js
cp /tmp/clinical_fix_deploy/apps/ui/app/clinical/consultation/controllers/investigationController.js /opt/emr/apps/ui/app/clinical/consultation/controllers/investigationController.js

echo "[3/4] Setting permissions..."
chmod 644 /opt/emr/apps/ui/app/common/util/httpErrorInterceptor.js
chmod 644 /opt/emr/apps/ui/app/clinical/app.js
chmod 644 /opt/emr/apps/ui/app/clinical/index.html
chmod 644 /opt/emr/apps/ui/app/clinical/consultation/views/orders.html
chmod 644 /opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js
chmod 644 /opt/emr/apps/ui/app/clinical/consultation/controllers/investigationController.js

echo "[4/4] Verifying content in bahmni-web container..."
docker exec bahmni-standard-bahmni-web-1 grep -n "openelis" /usr/local/apache2/htdocs/bahmni/common/util/httpErrorInterceptor.js
docker exec bahmni-standard-bahmni-web-1 grep -n "ignoreErrors" /usr/local/apache2/htdocs/bahmni/clinical/consultation/controllers/orderController.js
echo "DEPLOYMENT COMPLETE!"
