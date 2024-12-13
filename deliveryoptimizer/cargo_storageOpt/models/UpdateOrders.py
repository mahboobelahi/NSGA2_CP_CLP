from .OrderForm import FormData  

#from cargo_storageOpt.models.updateOrders import reset_order_fetched_for_range
def reset_order_fetched_for_range(start_id, end_id, flage=False, SR=0.85):
    """
    Updates the order_fetched field and supportRatio for all orders with ID between start_id and end_id.
    """
    try:
        # Fetch orders in the specified range
        orders = FormData.objects.filter(id__gte=start_id, id__lte=end_id)

        # Check if any records were found
        if not orders.exists():
            print(f"No orders found in the specified range {start_id} to {end_id}.")
            return

        # Update the fields
        rows_updated = orders.update(order_fetched=flage, supportRatio=SR)

        # Print the number of updated records and confirm changes
        print(f"Updated {rows_updated} orders with order_fetched set to {flage} and supportRatio set to {SR}.")

        # Verify the updates
        for order in FormData.objects.filter(id__gte=start_id, id__lte=end_id):
            print(f"ID: {order.id}, order_fetched: {order.order_fetched}, supportRatio: {order.supportRatio}")

    except Exception as e:
        print(f"An error occurred: {e}")

