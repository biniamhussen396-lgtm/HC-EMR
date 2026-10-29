#!/bin/bash
set -e

echo "[1/6] Extracting deployment archive..."
rm -rf /tmp/emr_deploy
mkdir -p /tmp/emr_deploy
tar -xzf /tmp/emr_deploy.tar.gz -C /tmp/emr_deploy

echo "[2/6] Ensuring remote directories exist..."
mkdir -p /opt/emr/apps/ui/app/orders/views
mkdir -p /opt/emr/apps/ui/app/orders/controllers
mkdir -p /opt/emr/apps/ui/app/admin/views
mkdir -p /opt/emr/apps/ui/app/admin/controllers
mkdir -p /opt/emr/apps/ui/app/common/concept-set/directives
mkdir -p /opt/emr/apps/ui/app/common/concept-set/services
mkdir -p /opt/emr/apps/ui/app/common/concept-set/views
mkdir -p /opt/emr/apps/ui/app/clinical/dashboard/views
mkdir -p /opt/emr/apps/ui/app/clinical/consultation/views/orderTemplateViews
mkdir -p /opt/emr/apps/ui/app/clinical/consultation/controllers
mkdir -p /opt/emr/config/openmrs/apps/orders
mkdir -p /opt/emr/config/openmrs/apps/admin
mkdir -p /opt/emr/config/openmrs/apps/home
mkdir -p /opt/emr/bahmni-docker/bahmni-standard
mkdir -p /opt/emr/backups

echo "[3/6] Deploying files into /opt/emr/ ..."
cp /tmp/emr_deploy/apps/ui/app/orders/views/orderSearch.html /opt/emr/apps/ui/app/orders/views/orderSearch.html
cp /tmp/emr_deploy/apps/ui/app/orders/controllers/orderSearchController.js /opt/emr/apps/ui/app/orders/controllers/orderSearchController.js
cp /tmp/emr_deploy/apps/ui/app/orders/app.js /opt/emr/apps/ui/app/orders/app.js
cp /tmp/emr_deploy/apps/ui/app/orders/index.html /opt/emr/apps/ui/app/orders/index.html
cp /tmp/emr_deploy/apps/ui/app/orders/views/orderFulfillment.html /opt/emr/apps/ui/app/orders/views/orderFulfillment.html
cp /tmp/emr_deploy/apps/ui/app/orders/controllers/orderFulfillmentController.js /opt/emr/apps/ui/app/orders/controllers/orderFulfillmentController.js
cp /tmp/emr_deploy/apps/ui/app/orders/initialization.js /opt/emr/apps/ui/app/orders/initialization.js
cp /tmp/emr_deploy/apps/ui/app/orders/orderFulfillmentConfig.js /opt/emr/apps/ui/app/orders/orderFulfillmentConfig.js
cp /tmp/emr_deploy/apps/ui/app/common/concept-set/directives/conceptSet.js /opt/emr/apps/ui/app/common/concept-set/directives/conceptSet.js
cp /tmp/emr_deploy/apps/ui/app/common/concept-set/services/conceptSetServices.js /opt/emr/apps/ui/app/common/concept-set/services/conceptSetServices.js
cp /tmp/emr_deploy/apps/ui/app/common/concept-set/views/conceptSet.html /opt/emr/apps/ui/app/common/concept-set/views/conceptSet.html
cp /tmp/emr_deploy/config/openmrs/apps/orders/app.json /opt/emr/config/openmrs/apps/orders/app.json
cp /tmp/emr_deploy/config/openmrs/apps/orders/extension.json /opt/emr/config/openmrs/apps/orders/extension.json
cp /tmp/emr_deploy/apps/ui/app/admin/views/backupRestore.html /opt/emr/apps/ui/app/admin/views/backupRestore.html
cp /tmp/emr_deploy/apps/ui/app/admin/controllers/backupRestoreController.js /opt/emr/apps/ui/app/admin/controllers/backupRestoreController.js
cp /tmp/emr_deploy/bahmni-docker/bahmni-standard/bahmni_backup_service.py /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py
cp /tmp/emr_deploy/apps/ui/app/admin/views/branding.html /opt/emr/apps/ui/app/admin/views/branding.html
cp /tmp/emr_deploy/apps/ui/app/admin/controllers/brandingController.js /opt/emr/apps/ui/app/admin/controllers/brandingController.js
cp /tmp/emr_deploy/apps/ui/app/admin/app.js /opt/emr/apps/ui/app/admin/app.js
cp /tmp/emr_deploy/apps/ui/app/admin/index.html /opt/emr/apps/ui/app/admin/index.html
cp /tmp/emr_deploy/config/openmrs/apps/admin/extension.json /opt/emr/config/openmrs/apps/admin/extension.json
cp /tmp/emr_deploy/config/openmrs/apps/branding.json /opt/emr/config/openmrs/apps/branding.json
cp /tmp/emr_deploy/config/openmrs/apps/home/whiteLabel.json /opt/emr/config/openmrs/apps/home/whiteLabel.json
cp /tmp/emr_deploy/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html /opt/emr/apps/ui/app/clinical/dashboard/views/clinicalDashboardHeader.html
cp /tmp/emr_deploy/apps/ui/app/clinical/consultation/views/orders.html /opt/emr/apps/ui/app/clinical/consultation/views/orders.html
cp /tmp/emr_deploy/apps/ui/app/clinical/consultation/controllers/orderController.js /opt/emr/apps/ui/app/clinical/consultation/controllers/orderController.js
cp /tmp/emr_deploy/apps/ui/app/clinical/consultation/views/orderTemplateViews/ordersTemplate.html /opt/emr/apps/ui/app/clinical/consultation/views/orderTemplateViews/ordersTemplate.html

chmod -R 644 /opt/emr/apps/ui/app/orders/
chmod -R 644 /opt/emr/apps/ui/app/admin/
chmod -R 644 /opt/emr/apps/ui/app/common/concept-set/
chmod -R 644 /opt/emr/config/openmrs/apps/
chmod 755 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py

echo "[4/6] Setting up systemd service bahmni-backup.service..."
cat << 'EOF' > /etc/systemd/system/bahmni-backup.service
[Unit]
Description=Bahmni Backup and Restore Service Daemon
After=network.target docker.service
Requires=docker.service

[Service]
Type=simple
User=root
WorkingDirectory=/opt/emr/bahmni-docker/bahmni-standard
ExecStart=/usr/bin/python3 /opt/emr/bahmni-docker/bahmni-standard/bahmni_backup_service.py --daemon
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now bahmni-backup.service
systemctl restart bahmni-backup.service

echo "[5/6] Ensuring OpenMRS DB privileges and search queries..."
docker exec bahmni-standard-openmrsdb-1 mysql -uroot -p"adminAdmin!123" openmrs -e "
INSERT IGNORE INTO privilege (privilege, description, uuid) VALUES 
('app:admin:restore', 'Bahmni Admin: Privilege to restore system backups and access restore operations', UUID()), 
('app:admin:deleteBackup', 'Bahmni Admin: Privilege to delete backup archives', UUID()); 
INSERT IGNORE INTO role_privilege (role, privilege) VALUES 
('SuperAdmin', 'app:admin:restore'), ('SuperAdmin', 'app:admin:deleteBackup'), 
('System Developer', 'app:admin:restore'), ('System Developer', 'app:admin:deleteBackup'), 
('Privilege Level: Full', 'app:admin:restore'), ('Privilege Level: Full', 'app:admin:deleteBackup');
"

echo "[6/6] Cleaning up temp deployment files..."
rm -rf /tmp/emr_deploy /tmp/emr_deploy.tar.gz
echo "DEPLOYMENT_FILES_INSTALLED_OK"
