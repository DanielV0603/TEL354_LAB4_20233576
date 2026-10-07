from select import select
import yaml
import json
import requests
import asyncio
import aiohttp

CONTROLLER_IP = "127.0.0.1"

class Student:
    # ADD YOUR CODE HERE
    def __init__(self, name , mac):
        self.name = name
        self.mac = mac
    
    def __str__(self):
        return f"{self.name} (MAC: {self.mac})"

    

class Service:
    # ADD YOUR CODE HERE
    def __init__(self, name, protocol, port):
        self.name = name
        self.protocol = protocol
        self.port = port
    
    def __str__(self):
        return f"{self.name} ({self.protocol}/{self.port})"

class Server:
    # ADD YOUR CODE HERE
    def __init__(self, name, ip, services_list = None):
        self.name = name
        self.ip = ip
        self.services = []
        if services_list:
            for s in services_list:
                self.services.append(Service(s['name'], s['protocol'], s['port']))

class Course:
    # ADD YOUR CODE HERE
    def __init__(self, name, code, state, students=None, servers=None):
        self.name = name
        self.code = code
        self.state = state
        self.students = students if students else []
        self.servers = servers if servers else []

    def mostrar_detalles(self):
        print(f"\n--- Detalles del Curso: {self.name}")
        print(f" Codigo: {self.code}")
        print(f" Estado: {self.state}")
        print("Alumnos inscritos:")
        for a in self.students:
            print(f"  - {a}")
            print(" Servidores permitidos:")
        for s in self.servers:
            servicios_permitidos = ", ".join(s.get('allowed_services', []))
            print(f"  - {s['name']} (Servicios: {servicios_permitidos})")
        print("------------------------------------------------------\n")

    def agregar_alumno(self, student_name):
        if student_name not in self.students:
            self.students.append(student_name)
            print(f"[*] Alumno {student_name} agregado al curso {self.code}.")
        else:
            print(f"[!] El alumno {student_name} ya está en el curso.")

    def remover_alumno(self, student_name):
        if student_name in self.students:
            self.students.remove(student_name)
            print(f"[*] Alumno {student_name} removido del curso {self.code}.")
        else:
            print("[!] Alumno no encontrado en la lista de este curso.")
    


def load_data(filename):
    with open(filename, "r") as file:
        data = yaml.safe_load(file)
    students = [ Student(x["name"], x["mac"]) for x in data["students"] ]
    servers = [ Server(y["name"], y["ip"], y["services"]) for y in data["servers"] ]
    courses = []
    for z in data.get("courses", []):
        courses.append(Course(
            name=z["name"], 
            code=z["code"], 
            state=z["state"], 
            students=z.get("students", []), 
            servers=z.get("servers", [])
        ))
    return students, servers, courses


def get_attachment_point(controller_ip, mac):
    endpoint = '/wm/device/'
    url = 'http://' + controller_ip + ':8080' + endpoint
    response = requests.get(
        url,
        params={'mac': mac}
    )
    
    devices = response.json()
    if not devices:
        return None, None
        
    result = devices[0]
    attachment_points = result.get("attachmentPoint", [])

    if not attachment_points:
        return None, None

    attachment_point = attachment_points[0]
    return attachment_point["switchDPID"], attachment_point["port"]


def get_route(controller_ip, src_mac, dst_mac):
    src_sw_dpid, src_sw_port = get_attachment_point(controller_ip, src_mac)
    dst_sw_dpid, dst_sw_port = get_attachment_point(controller_ip, dst_mac)
    endpoint = f'/wm/topology/route/{src_sw_dpid}/{src_sw_port}/{dst_sw_dpid}/{dst_sw_port}/json'
    url = 'http://' + controller_ip + ':8080' + endpoint
    response = requests.get(url)
    return response.json()

def crear_alumno(students):
        print("\n--- Crear Nuevo Alumno ---")
        nombre = input("Ingrese el nombre del alumno: ")
        mac = input("Ingrese la dirección MAC (ej. 00:11:22:33:44:55): ")
        nuevo_alumno = Student(nombre, mac)
        students.append(nuevo_alumno)
        print(f"[*] Alumno '{nombre}' (MAC: {mac}) creado exitosamente.")

def listar_alumnos(students):
    print("\n--- Lista de Alumnos ---")
    if not students:
        print("No hay alumnos registrados.")
        return
    for i, s in enumerate(students):
        print(f" {i+1}. {s.name} - MAC: {s.mac}")

def mostrar_detalles_alumno(students):
    listar_alumnos(students)
    try:
        idx = int(input("\nSeleccione el número del alumno para ver detalles: ")) - 1
        if 0 <= idx < len(students):
            s = students[idx]
            print(f"\n--- Detalles del Alumno ---")
            print(f" Nombre: {s.name}")
            print(f" MAC: {s.mac}")
        else:
            print("[!] Selección inválida.")
    except ValueError:
        print("[!] Entrada inválida. Debe ingresar un número.")
    print()
#cursos
def listar_cursos(courses):
    print("\n--- Lista de Cursos ---")
    if not courses:
        print("No hay cursos registrados.")
        return
    for i, c in enumerate(courses):
        print(f" {i+1}. {c.name} ({c.code}) - Estado: {c.state}")

def mostrar_detalles_curso(courses):
    listar_cursos(courses)
    try:
        idx = int(input("\nSeleccione el número del curso para ver detalles: ")) - 1
        if 0 <= idx < len(courses):
            courses[idx].mostrar_detalles() 
        else:
            print("[!] Selección inválida.")
    except ValueError:
        print("[!] Entrada inválida.")

def gestionar_alumnos_curso(courses, students):
    listar_cursos(courses)
    try:
        idx = int(input("\nSeleccione el número del curso a gestionar: ")) - 1
        if 0 <= idx < len(courses):
            curso = courses[idx]
            print(f"\nGestionando alumnos para: {curso.name} ({curso.code})")
            print("1. Agregar alumno")
            print("2. Remover alumno")
            opcion = input("Seleccione una opción (1/2): ")
            
            if opcion == '1':
                listar_alumnos(students)
                idx_al = int(input("Seleccione el número del alumno a matricular: ")) - 1
                alumno = students[idx_al]
                curso.agregar_alumno(alumno.name)
            elif opcion == '2':
                nombre_al = input("Ingrese el nombre exacto del alumno a remover: ")
                curso.remover_alumno(nombre_al)
            else:
                print("[!] Opción inválida.")
        else:
            print("[!] Selección inválida.")
    except ValueError:
        print("[!] Entrada o selección inválida.")
#servidores
def listar_servidores(servers):
    print("\n--- Lista de Servidores ---")
    if not servers:
        print("No hay servidores registrados.")
        return
    for i, s in enumerate(servers):
        print(f" {i+1}. {s.name} - IP: {s.ip}")

def mostrar_servicios_servidor(servers):
    listar_servidores(servers)
    try:
        idx = int(input("\nSeleccione el número del servidor para ver sus servicios: ")) - 1
        if 0 <= idx < len(servers):
            s = servers[idx]
            print(f"\n--- Servicios habilitados en {s.name} [{s.ip}] ---")
            if not s.services:
                print(" No hay servicios registrados para este servidor.")
            for srv in s.services:
                print(f"  - {srv.name} (Protocolo: {srv.protocol}, Puerto: {srv.port})")
        else:
            print("[!] Selección inválida.")
    except ValueError:
        print("[!] Entrada inválida.")

def menu():
    # ADD YOUR CODE HERE
    print("\n######################################################")
    print("Network Policy manager de la UPSM")
    print("######################################################")
    print("\nSeleccione una opción:\n")
    print("1) Importar")
    print("2) Exportar")
    print("3) Cursos")
    print("4) Alumnos")
    print("5) Servidores")
    print("6) Políticas")
    print("7) Conexiones")
    print("8) Salir")
    return input(">>> ")

# Diccionario global para guardar las conexiones activas
conexiones_activas = {}

# Función asíncrona para insertar flujos concurrentemente usando aiohttp
async def push_flows_async(controller_ip, flows):
    url = f"http://{controller_ip}:8080/wm/staticflowpusher/json"
    async with aiohttp.ClientSession() as session:
        tareas = [session.post(url, json=f) for f in flows]
        resultados = await asyncio.gather(*tareas)
        for r in resultados:
            if r.status not in [200, 201]:
                print(f"[!] Error insertando flujo. Código HTTP: {r.status}")

def listar_conexiones():
    print("\n--- Conexiones Activas ---")
    if not conexiones_activas:
        print("No hay conexiones activas.")
    for handler in conexiones_activas:
        print(f" - {handler}")

async def delete_flows_async(controller_ip, flows):
    url = f"http://{controller_ip}:8080/wm/staticflowpusher/json"
    async with aiohttp.ClientSession() as session:
        tareas = [session.delete(url, json={"name": f["name"]}) for f in flows]
        await asyncio.gather(*tareas)

def borrar_conexion(controller_ip=CONTROLLER_IP):
    listar_conexiones()
    if conexiones_activas:
        h = input("\nIngrese el nombre exacto del Handler a borrar: ")
        if h in conexiones_activas:
            # Llama a la función asíncrona para borrar los flujos en los switches
            asyncio.run(delete_flows_async(controller_ip, conexiones_activas[h]))
            # Lo elimina del diccionario local
            del conexiones_activas[h]
            print(f"[*] Flujos del handler '{h}' eliminados de la red.")
        else:
            print("[!] Handler no encontrado.")
    

def build_route(src_mac, dst_mac, servidor_ip, servicio, handler, controller_ip=CONTROLLER_IP):
    route = get_route(controller_ip, src_mac, dst_mac)
    
    if not route:
        print("[!] No se pudo calcular la ruta. Asegúrate de hacer ping entre las máquinas primero.")
        return None

    flows = []
    switches_procesados = set()

    # Iterar sobre todos los switches de la ruta obtenida
    for node in route:
        # Extraer el ID del switch 
        sw_dpid = node.get("switchDPID", node.get("switch", node.get("node")))
        
        if not sw_dpid or sw_dpid in switches_procesados:
            continue
        switches_procesados.add(sw_dpid)

        # Nombre único por switch para evitar sobreescritura
        sw_id = sw_dpid[-2:] 

        # Flujos
        flows.extend([
            {"switch": sw_dpid, "name": f"{handler}_{sw_id}_arp", "cookie": "0", "priority": "32768", 
             "eth_type": "0x0806", "active": "true", "actions": "output=normal"},
             
            {"switch": sw_dpid, "name": f"{handler}_{sw_id}_req", "cookie": "0", "priority": "32768",
             "eth_type": "0x0800", "ipv4_dst": servidor_ip, "ip_proto": "6" if servicio.protocol == "TCP" else "17",
             "tcp_dst": str(servicio.port), "active": "true", "actions": "output=normal"},
             
            {"switch": sw_dpid, "name": f"{handler}_{sw_id}_res", "cookie": "0", "priority": "32768",
             "eth_type": "0x0800", "ipv4_src": servidor_ip, "ip_proto": "6" if servicio.protocol == "TCP" else "17",
             "tcp_src": str(servicio.port), "active": "true", "actions": "output=normal"}
        ])
        
    # Insertar asíncronamente
    asyncio.run(push_flows_async(controller_ip, flows))
    return flows

def crear_conexion(students, servers, courses, controller_ip=CONTROLLER_IP):
    print("\n--- Crear Conexión ---")
    listar_alumnos(students)
    idx_al = int(input("Seleccione número del alumno: ")) - 1
    alumno = students[idx_al]
    
    listar_servidores(servers)
    idx_srv = int(input("Seleccione número del servidor: ")) - 1
    servidor = servers[idx_srv]
    
    print(f"\nServicios en {servidor.name}:")
    for i, srv in enumerate(servidor.services):
        print(f" {i+1}. {srv.name} ({srv.protocol}/{srv.port})")
    idx_serv = int(input("Seleccione número del servicio: ")) - 1
    servicio = servidor.services[idx_serv]
    
    # Validar Políticas
    autorizado = False
    for c in courses:
        if c.state == "ACTIVE" and alumno.name in c.students:
            for s in c.servers:
                if s['name'] == servidor.name and servicio.name in s.get('allowed_services', []):
                    autorizado = True
                    break
                    
    if not autorizado:
        print(f"[!] DENEGADO: El alumno no está autorizado o el curso está inactivo.")
        return
        
    print("[*] Autorizado. Calculando ruta...")
    dst_mac = input("Ingrese la MAC del servidor destino (Ej. la MAC de H3): ")
    handler = f"{alumno.name.replace(' ','_')}_TO_{servidor.name.replace(' ','_')}_{servicio.name}"
    
    # Llamamos a build_route respetando la instrucción de la guía
    flows_generados = build_route(alumno.mac, dst_mac, servidor.ip, servicio, handler, controller_ip)
    
    if flows_generados:
        conexiones_activas[handler] = flows_generados
        print(f"[*] Conexión instalada. Handler: {handler}")


def main():
    # Load data
    students, servers, courses = load_data("database.yaml")
    # print(get_attachment_point('10.100.18.253','a2:9a:f5:03:a0:65'))
    # print(json.dumps(get_route('10.100.18.253', "e6:3e:13:dc:ed:37","a6:96:21:fb:ca:a7"), indent=4))

    # ADD YOUR CODE HERE
    while True:
        opcion = menu()
        
        if opcion == '1':
            print("[*] (Función de Importar no requerida explícitamente)")
        
        elif opcion == '2':
            print("[*] (Función de Exportar no requerida explícitamente)")
            
        elif opcion == '3':
            print("\n--- Submenú Cursos ---")
            print("1) Listar")
            print("2) Mostrar detalles")
            print("3) Gestionar alumnos")
            sub_op = input(">>> ")
            if sub_op == '1': 
                listar_cursos(courses)
            elif sub_op == '2': 
                mostrar_detalles_curso(courses)
            elif sub_op == '3': 
                gestionar_alumnos_curso(courses, students)
            else: 
                print("[!] Opción inválida.")
                
        elif opcion == '4':
            print("\n--- Submenú Alumnos ---")
            print("1) Crear")
            print("2) Listar")
            print("3) Mostrar detalles")
            sub_op = input(">>> ")
            if sub_op == '1': 
                crear_alumno(students)
            elif sub_op == '2': 
                listar_alumnos(students)
            elif sub_op == '3': 
                mostrar_detalles_alumno(students)
            else: 
                print("[!] Opción inválida.")
                
        elif opcion == '5':
            print("\n--- Submenú Servidores ---")
            print("1) Listar")
            print("2) Mostrar servicios")
            sub_op = input(">>> ")
            if sub_op == '1': 
                listar_servidores(servers)
            elif sub_op == '2': 
                mostrar_servicios_servidor(servers)
            else: 
                print("[!] Opción inválida.")
                
        elif opcion == '6':
            print("[*] (Menú de Políticas no requerido)")
            
        elif opcion == '7':
            print("\n--- Submenú Conexiones ---")
            print("1) Crear")
            print("2) Listar")
            print("3) Borrar")
            print("[!] (Funcionalidades de conexión pendientes de implementar)")
            sub_op = input(">>> ")
            if sub_op == '1':
                crear_conexion(students, servers, courses)
            elif sub_op == '2':
                listar_conexiones()
            elif sub_op == '3':
                borrar_conexion()
        elif opcion == '8':
            print("Saliendo del Network Policy Manager...")
            break
            
        else:
            print("[!] Opción no reconocida. Intente nuevamente.")    

if __name__ == "__main__":
    main()
