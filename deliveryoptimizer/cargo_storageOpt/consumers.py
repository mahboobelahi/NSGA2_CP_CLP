import json
import logging
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
from .models.GAComputationResults import GAResult

logger = logging.getLogger(__name__)


class FlagConsumer(WebsocketConsumer):
    def connect(self):
        logger.info("WebSocket connection accepted.")
        async_to_sync(self.channel_layer.group_add)(
            "NSGA_flag_group",  # Group name
            self.channel_name
        )
        self.accept()  # Accept WebSocket connection

    def disconnect(self, close_code):
        logger.info("WebSocket connection closed.")
        async_to_sync(self.channel_layer.group_discard)(
            "NSGA_flag_group",  # Group name
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.send(text_data=json.dumps({
            'message': data['message']
        }))

    def send_flag(self):
        async_to_sync(self.channel_layer.group_send)(
            "NSGA_flag_group",  # Group name
            {
                "type": "send_flag_message",  # This type must match the handler method name
                "message": "Computation Completed!",
                "is_computing": True
            }
        )

    # The method to send message to WebSocket client
    def send_flag_message(self, event):
        message = event["message"]
        is_computing = event["is_computing"]

        # Send message and flag to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'is_computing': is_computing
        }))
        print("[XXXX]Flage sendt",is_computing)
#! Spin-flag
class SpinFlagConsumer(WebsocketConsumer):
    def connect(self):
        logger.info("WebSocket connection accepted.")
        async_to_sync(self.channel_layer.group_add)(
            "Spin_flag_group",  # Group name
            self.channel_name
        )
        self.accept()  # Accept WebSocket connection

    def disconnect(self, close_code):
        logger.info("WebSocket connection closed.")
        async_to_sync(self.channel_layer.group_discard)(
            "Spin_flag_group",  # Group name
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        self.send(text_data=json.dumps({
            'message': data['message']
        }))

    def send_flag(self):
        async_to_sync(self.channel_layer.group_send)(
            "Spin_flag_group",  # Group name
            {
                "type": "send_flag_message",  # This type must match the handler method name
                "message": "Computation Completed!",
                "is_computing": False
            }
        )

    # The method to send message to WebSocket client
    def send_flag_message(self, event):
        message = event["message"]
        is_computing = event["is_computing"]

        # Send message and flag to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'is_computing': is_computing
        }))
        

#! AR consumer

class ARConsumer(WebsocketConsumer):
    def connect(self):
        logger.info("WebSocket connection for AR accepted.")
        async_to_sync(self.channel_layer.group_add)(
            "ar_group",  # Group name for AR
            self.channel_name
        )
        self.accept()  # Accept the WebSocket connection
        sorted_results = GAResult.objects.order_by('-id')
        latest_result = sorted_results.first()
        ga_results= latest_result.get_result_json()
               
        self.send(text_data=json.dumps({
            'ga_results': ga_results
        }))
    def disconnect(self, close_code):
        logger.info("WebSocket connection for AR closed.")
        async_to_sync(self.channel_layer.group_discard)(
            "ar_group",  # Group name for AR
            self.channel_name
        )

    def receive(self, text_data):
        logger.info("Message received in ARConsumer.")  # Optional log for received messages
        pass  # Implement logic if you expect to receive messages

    def send_ga_results(self, event):
        ga_results = event.get("ga_results")
        # print(f"event.layout----{event}")
        # Send the layouts data to the WebSocket client
        self.send(text_data=json.dumps({
            'ga_results': ga_results#ga_results
        }))
