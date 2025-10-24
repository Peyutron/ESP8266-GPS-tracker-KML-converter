# gps_converter.py
import requests
import json
import os
from datetime import datetime

class GPXExporter:
    """Exportador a formato GPX"""
    
    def __init__(self):
        self.gpx_header = """<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="WEMOS D1 Mini GPS" 
     xmlns="http://www.topografix.com/GPX/1/1"
     xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
     xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd">
"""
        self.gpx_footer = "</gpx>"
    
    def _format_timestamp(self, date_str, time_str):
        """Convierte fecha/hora GPS a formato ISO 8601"""
        try:
            if len(date_str) == 6:
                day = date_str[:2]
                month = date_str[2:4]
                year = "20" + date_str[4:6]
                formatted_date = f"{year}-{month}-{day}"
            else:
                formatted_date = datetime.now().strftime("%Y-%m-%d")
            
            if len(time_str) >= 6:
                hours = time_str[:2]
                minutes = time_str[2:4]
                seconds = time_str[4:6]
                formatted_time = f"{hours}:{minutes}:{seconds}"
            else:
                formatted_time = "00:00:00"
            
            return f"{formatted_date}T{formatted_time}Z"
        except:
            return datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    def convert_json_to_gpx(self, json_data, track_name="Ruta WEMOS GPS"):
        """Convierte JSON a GPX"""
        gpx_content = self.gpx_header
        
        # Metadatos
        gpx_content += f"  <metadata>\n"
        gpx_content += f"    <name>{track_name}</name>\n"
        gpx_content += f"    <desc>Datos GPS capturados con WEMOS D1 Mini</desc>\n"
        gpx_content += f"    <time>{datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ')}</time>\n"
        gpx_content += f"  </metadata>\n"
        
        # Track
        gpx_content += f"  <trk>\n"
        gpx_content += f"    <name>{track_name}</name>\n"
        gpx_content += f"    <desc>Track con {len(json_data)} puntos GPS</desc>\n"
        gpx_content += f"    <trkseg>\n"
        
        # Puntos del track
        for i, point in enumerate(json_data):
            try:
                lat = point.get('lat', 0)
                lng = point.get('lng', 0)
                
                timestamp = self._format_timestamp(
                    point.get('dat', '010124'), 
                    point.get('tim', '00000000')
                )
                
                gpx_content += f"      <trkpt lat=\"{lat:.6f}\" lon=\"{lng:.6f}\">\n"
                gpx_content += f"        <ele>{point.get('alt', 0):.1f}</ele>\n"
                gpx_content += f"        <time>{timestamp}</time>\n"
                gpx_content += f"        <speed>{point.get('spe', 0):.3f}</speed>\n"
                gpx_content += f"        <extensions>\n"
                gpx_content += f"          <satellites>{point.get('sat', '0')}</satellites>\n"
                gpx_content += f"          <course>{point.get('cur', 0):.1f}</course>\n"
                gpx_content += f"        </extensions>\n"
                gpx_content += f"      </trkpt>\n"
                
            except Exception as e:
                print(f"  ⚠ Error en punto {i+1}: {e}")
                continue
        
        gpx_content += f"    </trkseg>\n"
        gpx_content += f"  </trk>\n"
        gpx_content += self.gpx_footer
        
        return gpx_content
    
    def save_gpx_file(self, gpx_content, filename):
        """Guarda archivo GPX"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(gpx_content)
            return True
        except Exception as e:
            print(f"Error guardando GPX: {e}")
            return False


class KMLExporter:
    """Exportador a formato KML"""
    
    def __init__(self):
        self.kml_header = """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
"""
        self.kml_footer = "</kml>"
    
    def convert_json_to_kml(self, json_data, route_name="Ruta WEMOS GPS"):
        """Convierte JSON a KML"""
        kml_content = self.kml_header
        kml_content += f"  <Document>\n"
        kml_content += f"    <name>{route_name}</name>\n"
        kml_content += f"    <description>Datos GPS capturados con WEMOS D1 Mini - {len(json_data)} puntos</description>\n"
        kml_content += f"    <open>1</open>\n"
        
        # Estilo de la ruta
        kml_content += f"    <Style id=\"routeStyle\">\n"
        kml_content += f"      <LineStyle>\n"
        kml_content += f"        <color>ff00ffff</color>\n"
        kml_content += f"        <width>4</width>\n"
        kml_content += f"      </LineStyle>\n"
        kml_content += f"    </Style>\n"
        
        # Línea de ruta
        kml_content += f"    <Placemark>\n"
        kml_content += f"      <name>{route_name}</name>\n"
        kml_content += f"      <description>Ruta completa con {len(json_data)} puntos GPS</description>\n"
        kml_content += f"      <styleUrl>#routeStyle</styleUrl>\n"
        kml_content += f"      <LineString>\n"
        kml_content += f"        <extrude>1</extrude>\n"
        kml_content += f"        <tessellate>1</tessellate>\n"
        kml_content += f"        <altitudeMode>absolute</altitudeMode>\n"
        kml_content += f"        <coordinates>\n"
        
        # Coordenadas
        coordinates = []
        for point in json_data:
            lat = point.get('lat', 0)
            lng = point.get('lng', 0)
            alt = point.get('alt', 0)
            coordinates.append(f"{lng:.6f},{lat:.6f},{alt:.1f}")
        
        kml_content += "          " + "\n          ".join(coordinates) + "\n"
        kml_content += f"        </coordinates>\n"
        kml_content += f"      </LineString>\n"
        kml_content += f"    </Placemark>\n"
        
        # Puntos individuales
        kml_content += f"    <Folder>\n"
        kml_content += f"      <name>Puntos GPS</name>\n"
        kml_content += f"      <open>0</open>\n"
        
        for i, point in enumerate(json_data):
            try:
                lat = point.get('lat', 0)
                lng = point.get('lng', 0)
                alt = point.get('alt', 0)
                
                description = f"""<![CDATA[
<h3>Punto GPS #{i+1}</h3>
<table>
<tr><td><b>Coordenadas:</b></td><td>{lat:.6f}, {lng:.6f}</td></tr>
<tr><td><b>Altitud:</b></td><td>{alt:.1f} m</td></tr>
<tr><td><b>Velocidad:</b></td><td>{point.get('spe', 0):.2f} km/h</td></tr>
<tr><td><b>Satélites:</b></td><td>{point.get('sat', '0')}</td></tr>
<tr><td><b>Rumbo:</b></td><td>{point.get('cur', 0):.1f}°</td></tr>
</table>
]]>"""
                
                kml_content += f"      <Placemark>\n"
                kml_content += f"        <name>Punto {i+1}</name>\n"
                kml_content += f"        <description>{description}</description>\n"
                kml_content += f"        <Point>\n"
                kml_content += f"          <altitudeMode>absolute</altitudeMode>\n"
                kml_content += f"          <coordinates>{lng:.6f},{lat:.6f},{alt:.1f}</coordinates>\n"
                kml_content += f"        </Point>\n"
                kml_content += f"      </Placemark>\n"
                
            except Exception as e:
                print(f"  ⚠ Error en punto {i+1}: {e}")
                continue
        
        kml_content += f"    </Folder>\n"
        kml_content += f"  </Document>\n"
        kml_content += self.kml_footer
        
        return kml_content
    
    def save_kml_file(self, kml_content, filename):
        """Guarda archivo KML"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(kml_content)
            return True
        except Exception as e:
            print(f"Error guardando KML: {e}")
            return False


class GPSConverter:
    """
    Clase principal para descargar y convertir datos GPS del WEMOS D1 Mini
    """
    
    def __init__(self, ip="192.168.4.1"):
        self.ip = ip
        self.base_url = f"http://{ip}"
        self.gpx_exporter = GPXExporter()
        self.kml_exporter = KMLExporter()
        self.current_json_data = None
        self.json_filename = "gps_data.json"
    
    def test_connection(self):
        """Prueba la conexión con el WEMOS"""
        try:
            response = requests.get(f"{self.base_url}/info", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def download_json_data(self, save_to_file=True):
        """Descarga datos JSON del WEMOS"""
        try:
            print("Conectando con WEMOS D1 Mini...")
            response = requests.get(f"{self.base_url}/download", timeout=10)
            
            if response.status_code == 200:
                json_data = []
                for line_num, line in enumerate(response.text.strip().split('\n'), 1):
                    if line.strip():
                        try:
                            json_data.append(json.loads(line))
                        except json.JSONDecodeError:
                            print(f"  Línea {line_num}: JSON inválido")
                            continue
                
                print(f"Datos descargados: {len(json_data)} registros")
                
                # Guardar en memoria
                self.current_json_data = json_data
                
                # Guardar en archivo si se solicita
                if save_to_file and json_data:
                    with open(self.json_filename, 'w', encoding='utf-8') as f:
                        for item in json_data:
                            json.dump(item, f)
                            f.write('\n')
                    print(f"JSON guardado: {self.json_filename}")
                
                return json_data
            else:
                print(f"Error en descarga: Código {response.status_code}")
                return None
                
        except requests.exceptions.ConnectionError:
            print("No se puede conectar al WEMOS")
            print("Verifica:")
            print("1. Estás conectado a la red 'gpsServer'")
            print("2. La contraseña es '!2345678'")
            print("3. El WEMOS está encendido")
            return None
        except Exception as e:
            print(f"Error inesperado: {e}")
            return None
    
    def load_json_from_file(self, filename=None):
        """Carga datos JSON desde archivo"""
        if filename:
            self.json_filename = filename
        
        try:
            if not os.path.exists(self.json_filename):
                print(f"Archivo no encontrado: {self.json_filename}")
                return None
            
            with open(self.json_filename, 'r', encoding='utf-8') as f:
                json_data = []
                for line_num, line in enumerate(f, 1):
                    if line.strip():
                        try:
                            json_data.append(json.loads(line))
                        except json.JSONDecodeError:
                            print(f"  ⚠ Línea {line_num}: JSON inválido")
                            continue
            
            self.current_json_data = json_data
            print(f"Datos cargados desde archivo: {len(json_data)} registros")
            return json_data
            
        except Exception as e:
            print(f"Error cargando archivo: {e}")
            return None
    
    def convert_current_data(self, output_format):
        """
        Convierte los datos actuales al formato especificado
        
        Args:
            output_format: "KML", "GPX", o "BOTH"
        """
        if not self.current_json_data:
            print("No hay datos cargados. Use la opción 1 primero.")
            return False
        
        success = True
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if output_format in ["KML", "BOTH"]:
            print("Convirtiendo a KML...")
            kml_content = self.kml_exporter.convert_json_to_kml(self.current_json_data)
            kml_filename = f"gps_data_{timestamp}.kml"
            if self.kml_exporter.save_kml_file(kml_content, kml_filename):
                print(f"🗺️  KML guardado: {kml_filename}")
            else:
                success = False
        
        if output_format in ["GPX", "BOTH"]:
            print("Convirtiendo a GPX...")
            gpx_content = self.gpx_exporter.convert_json_to_gpx(self.current_json_data)
            gpx_filename = f"gps_data_{timestamp}.gpx"
            if self.gpx_exporter.save_gpx_file(gpx_content, gpx_filename):
                print(f"GPX guardado: {gpx_filename}")
            else:
                success = False
        
        return success
    
    def get_file_info(self):
        """Obtiene información de los archivos del WEMOS"""
        try:
            response = requests.get(f"{self.base_url}/files", timeout=5)
            if response.status_code == 200:
                return json.loads(response.text)
        except:
            return None
    
    def get_current_data_info(self):
        """Obtiene información de los datos actuales"""
        if not self.current_json_data:
            return "No hay datos cargados"
        
        return f"{len(self.current_json_data)} registros GPS cargados"


def main():
    """
    Programa principal con menú interactivo
    """
    print("CONVERSOR GPS - WEMOS D1 MINI")
    print("=" * 50)
    
    converter = GPSConverter()
    
    while True:
        print("\n" + "=" * 50)
        print("MENÚ PRINCIPAL")
        print("=" * 50)
        print("ESTADO:", converter.get_current_data_info())
        print("-" * 50)
        print("1. Descargar datos del WEMOS (JSON)")
        print("2. Cargar datos desde archivo JSON")
        print("3. Convertir a KML (Google Earth)")
        print("4. Convertir a GPX (Dispositivos GPS)")
        print("5. Convertir a AMBOS formatos")
        print("6. Ver información del WEMOS")
        print("0. Salir")
        print("-" * 50)
        
        choice = input("Selecciona opción (0-6): ").strip()
        
        if choice == "1":
            # Descargar datos del WEMOS
            if converter.test_connection():
                converter.download_json_data(save_to_file=True)
            else:
                print("No se puede conectar al WEMOS")
        
        elif choice == "2":
            # Cargar desde archivo
            filename = input("Nombre del archivo JSON [gps_data.json]: ").strip()
            if not filename:
                filename = "gps_data.json"
            converter.load_json_from_file(filename)
        
        elif choice == "3":
            # Convertir a KML
            if converter.current_json_data:
                converter.convert_current_data("KML")
            else:
                print("Primero descarga o carga datos (opción 1 o 2)")
        
        elif choice == "4":
            # Convertir a GPX
            if converter.current_json_data:
                converter.convert_current_data("GPX")
            else:
                print("Primero descarga o carga datos (opción 1 o 2)")
        
        elif choice == "5":
            # Convertir a ambos
            if converter.current_json_data:
                converter.convert_current_data("BOTH")
            else:
                print("Primero descarga o carga datos (opción 1 o 2)")
        
        elif choice == "6":
            # Información del WEMOS
            if converter.test_connection():
                info = converter.get_file_info()
                if info:
                    print("\n📊 INFORMACIÓN DEL WEMOS:")
                    print(f"   Espacio total: {info.get('totalBytes', 0):,} bytes")
                    print(f"   Espacio usado: {info.get('usedBytes', 0):,} bytes")
                    print(f"   Archivos: {len(info.get('files', []))}")
                    for file_info in info.get('files', []):
                        print(f"     - {file_info.get('name', '')}: {file_info.get('size', 0):,} bytes")
                else:
                    print("❌ No se pudo obtener la información")
            else:
                print("❌ No hay conexión con el WEMOS")
        
        elif choice == "0":
            print("Bye!")
            break
        
        else:
            print("Opción no válida")
        
        if choice != "7":
            input("\nPresiona Enter para continuar...")


if __name__ == "__main__":
    main()