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
import threading
from pprint import pprint
from ..CLP_GA.configurations import config_dict

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
    NUM_OF_INDIVIDUALS = config_dict["NUM_OF_INDIVIDUALS"]
    NUM_OF_GENERATIONS = config_dict["NUM_OF_GENERATIONS"]#00#50
    PC = config_dict["PC"]
    PM1 = config_dict["PM1"]
    PM2 = config_dict["PM2"]
    K = config_dict["K"]
    ROTATIONS = config_dict["ROTATIONS"]
    if request.method == 'POST':
        try:
            unfetched_records = FormData.objects.filter(order_fetched=False)#!ORDERS
            print(unfetched_records)
            if unfetched_records:
                for record in unfetched_records:
                    record.order_fetched = True
                    record.save() 
                t = threading.Timer(1, main, args=(NUM_OF_INDIVIDUALS, NUM_OF_GENERATIONS,ROTATIONS,
                                                    PC, PM1, PM2, K, unfetched_records))
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
            pass
            # Check if latest_result exists
            
            # channel_layer = get_channel_layer()
            # async_to_sync(channel_layer.group_send)(
            #     "ar_group",  # Group name for ARConsumer
            #     {
            #         "type": "send_ga_results",
            #         "ga_results": latest_result.get_result_json(),
                    
            #     }
            # )
            

            return JsonResponse({},safe=False) 
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