# """
# ASGI config for deliveryoptimizer project.

# It exposes the ASGI callable as a module-level variable named ``application``.

# For more information on this file, see
# https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
# """

# import os

# from django.core.asgi import get_asgi_application

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliveryoptimizer.settings')

# application = get_asgi_application()
#!!!!!!!!!!!!!!!!!!!!!!!!!Custome ASGI app setting !!!!!!!!!!!!!!!!!!!!!!!!!!
"""
ASGI config for deliveryoptimizer project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
# from ..cargo_storageOpt import websocket_urlpatterns


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'deliveryoptimizer.settings')

application = get_asgi_application()
from cargo_storageOpt.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": application,  # Handle traditional HTTP requests
    "websocket": 
        AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
})


