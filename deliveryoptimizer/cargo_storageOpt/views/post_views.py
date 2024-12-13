from rest_framework.decorators import api_view
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.http import JsonResponse
from pprint import pprint
from ..models.container import Container
from ..models.OrderForm import FormData
from ..models.GAComputationResults import GAResult
from ..serializers.serializers import FormDataSerializer
from ..CLP_GA.main import main
import threading,json
from django.views.decorators.csrf import csrf_exempt
from pprint import pprint


@api_view(['POST'])
def add_containers(request):
    try:
        # Parse the JSON body
        data = json.loads(request.body)

        # Check if the input is a list
        if not isinstance(data, list):
            return JsonResponse({'error': 'Expected a list of containers'}, status=400)

        # Validate and create containers
        required_fields = [
            'opening_type', 'cont_ID', 'sort_id', 'tare_weight', 'payload',
            'external_length', 'external_width', 'external_height',
            'internal_length', 'internal_width', 'internal_height'
        ]

        containers = []
        errors = []

        for idx, container_data in enumerate(data):
            missing_fields = [field for field in required_fields if field not in container_data]
            if missing_fields:
                errors.append({
                    'index': idx,
                    'error': f'Missing fields: {", ".join(missing_fields)}'
                })
                continue

            try:
                # Create a container object
                container = Container(
                    opening_type=container_data['opening_type'],
                    cont_ID=container_data['cont_ID'],
                    sort_id=container_data['sort_id'],
                    tare_weight=container_data['tare_weight'],
                    payload=container_data['payload'],
                    external_length=container_data['external_length'],
                    external_width=container_data['external_width'],
                    external_height=container_data['external_height'],
                    internal_length=container_data['internal_length'],
                    internal_width=container_data['internal_width'],
                    internal_height=container_data['internal_height']
                )
                containers.append(container)
            except Exception as e:
                errors.append({'index': idx, 'error': str(e)})

        # Bulk create containers
        if containers:
            Container.objects.bulk_create(containers)

        # Return response
        return JsonResponse({
            'message': f'{len(containers)} containers added successfully.',
            'errors': errors
        }, status=201 if containers else 400)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@api_view(['POST'])
def submit_order_info(request):
    pprint(request.data)
    if request.method == 'POST':
        try:
            serializer = FormDataSerializer(data=request.data)
            pprint(serializer)
            if serializer.is_valid():
                serializer.save()
                print(f"[X] OrderDataSaved")
                return Response(serializer.data)
            print("errors",serializer.errors)
            return Response({'error': str(serializer.errors)})
        except Exception as e:
            return Response({'error': str(e)})


@api_view(['POST'])
def compute(request):
    
    if request.method == 'POST':
        try:
            unfetched_records = FormData.objects.filter(order_fetched=False)#!ORDERS
            print(unfetched_records)
            if unfetched_records:
                for record in unfetched_records:
                    record.order_fetched = True
                    record.save()                 
                t = threading.Timer(1, main, args=(unfetched_records,))
                t.start() 

                return JsonResponse({'message': 'Computation started successfully'})
            else:
                return JsonResponse({'error': 'Please submit an order.'})
        except Exception as e:
            return JsonResponse({'error': str(e)})
    else:
        return JsonResponse({'error': 'Method not allowed'})

#! use database
@api_view(['POST'])
def handle_plot_data(request):
    try:
        row_data = request.data.get('rowData')
        print(f"[X] RoeData:{row_data}")
        ss_key = row_data.get("ss_key")
        sorted_results = GAResult.objects.order_by('-id')
        
        obj = Container.objects.get(cont_ID=row_data.get("containerId"))

        x_ticks, y_ticks, z_ticks = obj.get_external_dimensions().get("cm")
        ticks = {"x_ticks": x_ticks, "y_ticks": y_ticks,
                     "z_ticks": z_ticks, "step_size": 30}
        # Select the latest one (first one after sorting)
        latest_result = sorted_results.first()
        # print(latest_result.file_name)
        if latest_result:
            # Check if latest_result exists
            layouts= latest_result.get_layouts()
            plot_data = [rec.get("plot_data") for rec in layouts.get(ss_key).get("item_passport")]
            #plot_data = layouts.get(ss_key)
            # pprint(result_json)
            return JsonResponse({"plot_data": plot_data, "ticks": ticks,"ss_key":ss_key}, safe=False)#return JsonResponse(result_json, content_type='application/json', status=200, safe=False)
        else:
            # Return error response if no result is found
            return JsonResponse({'error': 'No GA result found'})

    except FileNotFoundError:
        return JsonResponse({'error': 'Solution data not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
#! after integrating with UI modify this function
@api_view(['POST'])
def historic_plot_data(request):
    if request.method == 'POST':
        try:
            print(request.data)
            file_name = request.data.get('file_name')
            ss_key = request.data.get('ss_key')
            record = GAResult.objects.get(file_name=file_name)
            plot_data = [rec.get("plot_data") for rec in record.get_layouts().get(ss_key).get("item_passport")]
            containerId = record.get_metadata().get("id")
            obj = Container.objects.get(cont_ID=containerId)
            x_ticks, y_ticks, z_ticks = obj.get_external_dimensions().get("cm")
            ticks = {"x_ticks": x_ticks, "y_ticks": y_ticks,
                        "z_ticks": z_ticks, "step_size": 30}
            return JsonResponse({"plot_data": plot_data, "ticks": ticks}, safe=False)
            
        except Exception as e:
            return JsonResponse({'error': str(e)})





@api_view(['POST'])
def handle_ar_view(request):
    try:
        sorted_results = GAResult.objects.order_by('-id')
        latest_result = sorted_results.first()
        # layouts= latest_result.get_layouts()
        if latest_result:
            print(f"[X] laatesResult: {latest_result}")
            pass
            return JsonResponse({"message":"Success"},safe=False) 
        #JsonResponse({"plot_data": plot_data, "ticks": ticks}, safe=False)#return JsonResponse(result_json, content_type='application/json', status=200, safe=False)
        else:
            # Return error response if no result is found
            return JsonResponse({'error': 'No GA result found'})

    except FileNotFoundError:
        return JsonResponse({'error': 'Solution data not found'})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    

@api_view(['POST'])
def generate_report(request):
    if request.method == 'POST':
        row_data = request.data.get('rowData')
        if row_data is not None:
            #pprint(row_data)
            return JsonResponse({'message': 'Comming Soon!'})#'Plot data received successfully'
        else:
            return JsonResponse({'error': 'rowData parameter not found in request'})












# @api_view(['POST'])
# def handle_plot_data(request):
#     if request.method == 'POST':
#         row_data = request.data.get('rowData')
#         print(row_data)
#         plot_data = []
#         try:
#             obj = Container.objects.get(cont_ID=row_data.get("containerId"))

#             x_ticks, y_ticks, z_ticks = obj.get_external_dimensions().get("cm")
#             ticks = {"x_ticks": x_ticks, "y_ticks": y_ticks,
#                      "z_ticks": z_ticks, "step_size": 30}
#             # Determine the path to the most recent result file
#             reports_dir = os.path.join('cargo_storageOpt', 'CLP_GA', 'Reports')
#             all_folders = [folder for folder in os.listdir(
#                 reports_dir) if os.path.isdir(os.path.join(reports_dir, folder))]
#             most_recent_folder = max(all_folders)
#             most_recent_folder_path = os.path.join(
#                 reports_dir, most_recent_folder)
#             recent_file = max(os.listdir(most_recent_folder_path), key=lambda x: os.path.getmtime(
#                 os.path.join(most_recent_folder_path, x)))
#             result_file_path = os.path.join(
#                 most_recent_folder_path, recent_file)

#             # Read the content of the most recent JSON file
#             with open(result_file_path, 'r') as f:
#                 res = json.load(f)

#             if row_data is not None:
#                 if res.get('layouts').get(row_data.get("ss_key")):
#                     plot_data = [rec.get("plot_data") for rec in res.get(
#                         'layouts').get(row_data.get("ss_key")).get("item_passport")]
#                 else:
#                     pprint(row_data)
#                     print(res.get('layouts').get(row_data.get("ss_key")))

#                 return JsonResponse({"plot_data": plot_data, "ticks": ticks}, safe=False)
#             else:
#                 return JsonResponse({'error': 'rowData parameter not found in request'}, status=400)
#         except Container.DoesNotExist:
#             # Handle the case where the object does not exist
#             return HttpResponseNotFound("Container not found")