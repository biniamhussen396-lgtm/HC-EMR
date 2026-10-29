
set -e
mkdir -p /tmp/referral_deploy
tar -xzf /tmp/referral_deploy.tar.gz -C /tmp/referral_deploy
cp /tmp/referral_deploy/config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql /opt/emr/config/masterdata/configuration/sql/emrapi.sqlSearch.referralManagement.sql
cp /tmp/referral_deploy/apps/ui/app/bedmanagement/app.js /opt/emr/apps/ui/app/bedmanagement/app.js
cp /tmp/referral_deploy/apps/ui/app/bedmanagement/index.html /opt/emr/apps/ui/app/bedmanagement/index.html
cp /tmp/referral_deploy/apps/ui/app/bedmanagement/controllers/referralManagementController.js /opt/emr/apps/ui/app/bedmanagement/controllers/referralManagementController.js
cp /tmp/referral_deploy/apps/ui/app/bedmanagement/views/referralManagement.html /opt/emr/apps/ui/app/bedmanagement/views/referralManagement.html
cp /tmp/referral_deploy/apps/ui/app/bedmanagement/controllers/referFormPrintController.js /opt/emr/apps/ui/app/bedmanagement/controllers/referFormPrintController.js
cp /tmp/referral_deploy/apps/ui/app/bedmanagement/views/referFormPrint.html /opt/emr/apps/ui/app/bedmanagement/views/referFormPrint.html

find /opt/emr/apps/ui/app/bedmanagement -type d -exec chmod 755 {} +
find /opt/emr/apps/ui/app/bedmanagement -type f -exec chmod 644 {} +
find /opt/emr/config/masterdata/configuration/sql -type f -exec chmod 644 {} +

rm -rf /tmp/referral_deploy /tmp/referral_deploy.tar.gz
echo "REFERRAL_FILES_COPIED_SUCCESS"
