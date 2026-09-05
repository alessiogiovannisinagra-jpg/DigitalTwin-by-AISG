import time
import random
import csv
import os
from datetime import datetime
from supabase import create_client, Client

# Le tue credenziali reali di Supabase
SUPABASE_URL = "https://kxcuinswyrrzpmlknejs.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imt4Y3VpbnN3eXJyenBtbGtuZWpzIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODg2MzI0NzgsImV4cCI6MjEwNDIwODQ3OH0._S5k8CEviqpUAFlFwD4bxhkcPdCozUhz4AWLamFutqw"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Nome del file di log locale (stile city_log.csv) per la tracciabilità aziendale
CSV_LOG_FILE = "city_log.csv"

def init_csv_log():
    if not os.path.exists(CSV_LOG_FILE):
        with open(CSV_LOG_FILE, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["Timestamp", "Device_ID", "Metric_Name", "Metric_Value", "Status"])

def log_to_local_csv(timestamp, device_id, metric_name, value, status):
    with open(CSV_LOG_FILE, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([timestamp, device_id, metric_name, value, status])

def avvio_digital_twin():
    print("=== Avvio Motore Digital Twin (Data Logger & IoT Bridge) ===")
    init_csv_log()
    
    # 1. Registriamo o recuperiamo un dispositivo di test sul database
    device_payload = {
        "name": "Smart Meter Impianto Principale",
        "client_name": "Azienda Cliente Demo",
        "device_type": "energy_meter",
        "status": "online",
        "metadata": {"location": "Stabilimento 1 - Settore Energia"}
    }
    
    try:
        response = supabase.table("devices").insert(device_payload).execute()
        device_id = response.data[0]["id"]
        print(f"Dispositivo connesso con successo. ID: {device_id}")
    except Exception as e:
        print(f"Errore nella connessione al dispositivo: {e}")
        return

    # 2. Ciclo di invio dati continuo (Simula il campo / IoT)
    try:
        while True:
            timestamp_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Generazione dati realistici di potenza attiva (kW) e temperatura (°C)
            potenza_kw = round(random.uniform(20.0, 55.5), 2)
            temperatura = round(random.uniform(40.0, 68.5), 1)
            
            # Invio telemetria 1: Potenza (alimenta il grafico sulla dashboard)
            supabase.table("device_telemetry").insert({
                "device_id": device_id,
                "metric_name": "power_kw",
                "metric_value": potenza_kw
            }).execute()

            # Invio telemetria 2: Temperatura
            supabase.table("device_telemetry").insert({
                "device_id": device_id,
                "metric_name": "temperature_c",
                "metric_value": temperatura
            }).execute()

            # Scrittura sul log locale CSV per conformità e verificabilità
            log_to_local_csv(timestamp_str, device_id, "power_kw", potenza_kw, "ONLINE")
            
            print(f"[{timestamp_str}] Dati inviati a Supabase & CSV -> Potenza: {potenza_kw} kW | Temperatura: {temperatura} °C")

            # Ogni tanto generiamo un log di sistema mirato (es. controllo efficienza)
            if random.random() < 0.25:
                desc = f"Verifica automatica efficienza energetica: carico stabile a {potenza_kw} kW."
                supabase.table("system_logs").insert({
                    "device_id": device_id,
                    "action_type": "ENERGY_OPTIMIZATION",
                    "description": desc,
                    "payload": {"power": potenza_kw}
                }).execute()
                print("--> Log di sistema registrato sul Cloud.")

            time.sleep(4)

    except KeyboardInterrupt:
        print("\nInterruzione rilevata. Imposto lo stato del dispositivo su 'offline'...")
        supabase.table("devices").update({"status": "offline"}).eq("id", device_id).execute()
        print("Dispositivo offline. Script terminato.")

if __name__ == "__main__":
    avvio_digital_twin()
