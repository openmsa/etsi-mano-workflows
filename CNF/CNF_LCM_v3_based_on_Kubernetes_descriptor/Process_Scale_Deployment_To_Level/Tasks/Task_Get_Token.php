<?php

require_once '/opt/fmc_repository/Process/Reference/Common/common.php';
require_once '/opt/fmc_repository/Process/Reference/OPENSTACK/Library/REST/openstack_common_rest.php';

function list_args()
{
}
if ($context['auth_method'] == "OPENSTACK"){
check_mandatory_param('user_domain_id');
check_mandatory_param('tenant_login');
check_mandatory_param('tenant_password');
check_mandatory_param('project_domain_id');
check_mandatory_param('tenant_id');
check_mandatory_param('keystone_public_endpoint');

$user_domain_id = $context['user_domain_id'];
$tenant_login = $context['tenant_login'];
$tenant_password = $context['tenant_password'];
$project_domain_id = $context['project_domain_id'];
$openstack_tenant_id = $context['tenant_id'];
$keystone_public_endpoint = $context['keystone_public_endpoint'];

$response = _keystone_project_scoped_token_get($keystone_public_endpoint, $user_domain_id, $tenant_login,$tenant_password, $project_domain_id, $openstack_tenant_id);



$response = json_decode($response, true);
if ($response['wo_status'] !== ENDED) {
        $response = json_encode($response);
        echo $response;
        exit;
}

$response_raw_headers = $response['wo_newparams']['response_raw_headers'];
$response_headers = http_parse_headers($response_raw_headers);
$token_id = $response_headers[X_SUBJECT_TOKEN];

$endpoints = $response['wo_newparams']['response_body']['token']['catalog'];
$context['endpoints'] = seperate_endpoints_v3($endpoints);

}
if ($context['auth_method'] == "KUBERNETES"){
$token_id = $context['kube_token'];
}
$context['token_id'] = $token_id;

$response = prepare_json_response(ENDED, "Token created successfully.\nToken Id : $token_id", $context, true);
echo $response;

?>
