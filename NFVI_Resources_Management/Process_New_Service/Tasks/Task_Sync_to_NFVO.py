from msa_sdk.variables import Variables
from msa_sdk.msa_api import MSA_API
from msa_sdk.order import Order

if __name__ == "__main__":

    dev_var = Variables()
    dev_var.add('nfvo_device', var_type='Device')
    dev_var.add("service_instance_name", var_type='String')
    context = Variables.task_call(dev_var)

    device_short_id = context['nfvo_device'][3:]

    order = Order(str(device_short_id))
    order.command_synchronize(timeout=60)

    ret = MSA_API.process_content('ENDED',
        f'Device {context["nfvo_device"]} synchronized', context, True)

    print(ret)