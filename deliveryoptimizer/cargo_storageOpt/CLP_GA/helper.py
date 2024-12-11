from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

def computation_complete(flag=False):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "NSGA_flag_group",  # Group name
        {
            "type": "send_flag_message",
            "message": "Computation Completed!",
            "is_computing": flag
        }
    )

def spinFlag(flag=True):

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        "Spin_flag_group",  # Group name
        {
            "type": "send_flag_message",
            "message": "Computation Completed!",
            "is_computing": flag
        }
    )