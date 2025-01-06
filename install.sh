#!/bin/bash
. /usr/share/install-libraries/il-lib.sh

#
# Shall we install python-sdk and php-sdk ?
#
pushd /opt/fmc_repository/Process || exit;

emit_step "WF references and libs"
mk_meta_link "php_sdk" "Reference"
emit_step "ETSI-MANO %b" "$TAG_WF_ETSI_MANO"
ln -fsn ../etsi-mano-workflows etsi-mano-workflows

popd || exit
unlink /opt/fmc_repository/Process/PythonReference/custom/ETSI
unlink /opt/fmc_repository/etsi-mano-workflows/src/src 2>/dev/null
ln -sf /opt/fmc_repository/etsi-mano-workflows/src /opt/fmc_repository/Process/PythonReference/custom/ETSI

