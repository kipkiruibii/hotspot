from routeros_api import RouterOsApiPool

def check_and_remove_queue_if_no_mac():
    try:
        connection = RouterOsApiPool(
            host="10.0.0.1",  # MikroTik's WireGuard IP
            username="api-user",
            password="@Dracula2025",
            port=8728,
            use_ssl=False,
            plaintext_login=True,
        )
        api = connection.get_api()
        queue = api.get_resource("/queue/simple")
        bypass = api.get_resource("/ip/hotspot/ip-binding")

        # Get all IP bindings (mac addresses)
        ip_bindings = bypass.get()

        # Iterate over all queues
        queues = queue.get()

        for q in queues:
            ip = q["target"].split("/")[0]  # Extract the IP from the target field

            # Check if there's any MAC address bound to this IP
            mac_found = False
            for binding in ip_bindings:
                if binding["address"] == ip:
                    mac_found = True
                    break

            # If no MAC address found, remove the queue
            if not mac_found:
                queue.remove(id=q["id"])
                print(f"Queue for IP {ip} removed as there's no MAC address bound.")

        connection.disconnect()

    except Exception as e:
        print(f"Error in checking/removing queue: {e}")

