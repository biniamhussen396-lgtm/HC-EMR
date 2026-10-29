
set -e
mkdir -p /tmp/payment_deploy
tar -xzf /tmp/payment_deploy.tar.gz -C /tmp/payment_deploy
cp /tmp/payment_deploy/apps/ui/app/admin/views/paymentConfig.html /opt/emr/apps/ui/app/admin/views/paymentConfig.html
cp /tmp/payment_deploy/apps/ui/app/admin/controllers/paymentConfigController.js /opt/emr/apps/ui/app/admin/controllers/paymentConfigController.js
cp /tmp/payment_deploy/apps/ui/app/admin/app.js /opt/emr/apps/ui/app/admin/app.js
cp /tmp/payment_deploy/apps/ui/app/admin/index.html /opt/emr/apps/ui/app/admin/index.html
cp /tmp/payment_deploy/config/openmrs/apps/admin/extension.json /opt/emr/config/openmrs/apps/admin/extension.json
cp /tmp/payment_deploy/bahmni-docker/bahmni-standard/bahmni_backup_service.py /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py
cp /tmp/payment_deploy/apps/ui/app/orders/controllers/orderFulfillmentController.js /opt/emr/apps/ui/app/orders/controllers/orderFulfillmentController.js
cp /tmp/payment_deploy/apps/ui/app/orders/views/orderFulfillment.html /opt/emr/apps/ui/app/orders/views/orderFulfillment.html
cp /tmp/payment_deploy/apps/ui/app/clinical/index.html /opt/emr/apps/ui/app/clinical/index.html
cp /tmp/payment_deploy/apps/ui/app/clinical/dashboard/controllers/patientDashboardController.js /opt/emr/apps/ui/app/clinical/dashboard/controllers/patientDashboardController.js

find /opt/emr/apps/ui/app/admin -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/admin -type f -exec chmod 644 {} +
find /opt/emr/apps/ui/app/orders -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/orders -type f -exec chmod 644 {} +
find /opt/emr/apps/ui/app/clinical -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/clinical -type f -exec chmod 644 {} +
find /opt/emr/config/openmrs/apps/admin -type f -exec chmod 644 {} +
chmod 755 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py

systemctl daemon-reload
systemctl restart bahmni-backup.service

rm -rf /tmp/payment_deploy /tmp/payment_deploy.tar.gz
echo "PAYMENT_DEPLOY_SUCCESS"
