import json
import asyncio
from gmqtt import Client as MQTTClient
from app.core.config import settings

class MQTTHandler:
    def __init__(self, schedule_service_factory):
        self.client = MQTTClient("backend_service")
        # factory này dùng để tạo session DB khi cần xử lý message
        self.schedule_service_factory = schedule_service_factory

    def on_connect(self, client, flags, rc, properties):
        print("[MQTT] Connected to Broker")
        # Subscribe vào topic mà các ESP32 sẽ gửi yêu cầu sync
        self.client.subscribe("school_bell/+/request_sync", qos=1)
        # Subscribe vào topic báo cáo trạng thái
        self.client.subscribe("school_bell/+/report", qos=1)

    async def on_message(self, client, topic, payload, qos, properties):
        try:
            topic_parts = topic.split("/")
            mac_address = topic_parts[1] # Lấy MAC từ topic
            msg_type = topic_parts[2]    # request_sync hoặc report
            
            payload_data = json.loads(payload.decode())
            print(f"[MQTT] Message from {mac_address}: {msg_type}")

            if msg_type == "request_sync":
                # Khi ESP32 xin lịch, ta gọi service để xào nấu dữ liệu
                async with self.schedule_service_factory() as service:
                    sync_data = await service.get_sync_data(mac_address)
                    # Bắn trả lại topic sync riêng của con ESP32 đó
                    self.client.publish(
                        f"school_bell/{mac_address}/sync",
                        json.dumps(sync_data),
                        qos=1,
                        retain=True
                    )
        except Exception as e:
            print(f"[MQTT] Error processing message: {e}")

    async def connect(self):
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        
        if settings.MQTT_USER:
            self.client.set_auth_credentials(settings.MQTT_USER, settings.MQTT_PASSWORD)
            
        await self.client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)

    def publish_command(self, mac: str, command: dict):
        """Hàm dùng cho API để bắn lệnh khẩn cấp hoặc lệnh khóa/mở"""
        self.client.publish(
            f"school_bell/{mac}/cmd",
            json.dumps(command),
            qos=1
        )