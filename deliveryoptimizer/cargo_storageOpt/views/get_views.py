
from django.http import JsonResponse, HttpResponse
from ..models.container import Container
from ..models.GAComputationResults import GAResult
from ..CLP_GA.main import main
from ..CLP_GA import configurations as CONFIG
from pprint import pprint


def default_message(request):
    # Extract necessary information from the request
    client_ip = get_client_ip(request)  # Helper function to get client IP
    user_agent = request.META.get('HTTP_USER_AGENT', 'Unknown')
    
    # Fetch all containers from the database
    containers = Container.objects.all()
    
    # Create container details as an HTML string
    container_info = "<br>".join([
        f"Container {cont.cont_ID}ft: Opening = {cont.get_opening_type_display()}, "
        f"Weight = {cont.tare_weight} kg, Payload = {cont.payload} kg, "
        f"External Length = {cont.external_length} m, "
        f"External Width = {cont.external_width} m, "
        f"External Height = {cont.external_height} m"
        for cont in containers
    ])
    
    # Add request details and container information to the HTML response
    html = (
        f"<html><body>"
        f"<h2>Request Details</h2>"
        f"<p>Client IP: {client_ip}</p>"
        f"<p>User Agent: {user_agent}</p>"
        f"<h2>Container Information</h2>"
        f"<p>{container_info}</p>"
        f"</body></html>"
    )
    
    return HttpResponse(html)

def get_client_ip(request):
    """Helper function to get the client IP address."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', 'Unknown')
    return ip


def get_cont_ids(request):
    try:
        print(f"X {[{'name': f'{cont.cont_ID}', 'id': cont.cont_ID} for cont in Container.objects.all()]}")
        return JsonResponse([{'name': f"{cont.get_cont_name()}", 'id': cont.cont_ID} for cont in Container.objects.all()],
                            safe=False)
    except Container.DoesNotExist:
        return JsonResponse({'error': 'Container not found'}, status=404)


def get_container_info(request, container_id=None):

    try:
        if container_id:
            cont = Container.objects.get(cont_ID=container_id)

            return JsonResponse(cont.get_info())
        else:
            containers = Container.objects.all()
            containers_info = [container.get_info() for container in containers]
            return JsonResponse({'containers': containers_info})
    except Container.DoesNotExist:
        return JsonResponse({'error': 'Container not found'}, status=404)
def get_results(request):
    try:
        sorted_results = GAResult.objects.order_by('-file_name')

        # Select the latest one (first one after sorting)
        latest_result = sorted_results.first()

        if latest_result:
            # Check if latest_result exists
            print(latest_result.file_name)
            result_json = latest_result.get_result_json()
            # pprint(result_json)
            return JsonResponse(result_json, content_type='application/json', status=200, safe=False)
        else:
            # Return error response if no result is found
            return JsonResponse({'error': 'No GA result found'})

    except FileNotFoundError:
        return JsonResponse({'error': 'Solution data not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})



def get_all_results_files(request):
    try:
        # Retrieve all GA result file names
        sorted_results = GAResult.objects.order_by('-file_name')
        file_names = [result.file_name for result in sorted_results]
        
        # Get layout keys for each result
        layout_keys = [list(result.get_layouts().keys()) for result in sorted_results]

        if file_names:
            # Combine file names and layout keys into a dictionary
            data = {
                'file_names': file_names,
                'layout_keys': layout_keys
            }
            # Return the combined data in the JSON response
            return JsonResponse(data, status=200)
        else:
            # Return error response if no result is found
            return JsonResponse({'error': 'No GA result found'})

    except FileNotFoundError:
        return JsonResponse({'error': 'Solution data not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})


