from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.device import Device

from custom.ETSI.NsLcmSol005 import NsLcmSol005
from custom.ETSI.NsdSol005 import NsdSol005


if __name__ == "__main__":

    dev_var = Variables()
    context = Variables.task_call(dev_var)
    
    #Get the checking NSD Id and the original NSD ID (stored during the instantiation) from the context.
    origin_nsd_id = context['nsd_id']
    checking_nsd_id = context['nsd_id_checking']
    
    if origin_nsd_id != checking_nsd_id:
        msg = 'The context nsd_id is different than the nsd_id specied in the NS Package from NFVO Catalog: ' + origin_nsd_id ' ==> ' + checking_nsd_id
        MSA_API.task_success(msg, context)
    
    msg = 'The context nsd_id is matched to the NS Package from NFVO Catalog.'
    MSA_API.task_success(msg, context)