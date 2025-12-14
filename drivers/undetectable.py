import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

# Defaults
address = "127.0.0.1"
port_from_settings_browser = '25325'
chrome_driver_path = "C:\chromedriver\chromedriver.exe"


def print_profiles_table(profiles):
    # profiles: list of (id, dict)
    if not profiles:
        return
    widths = (4, 36, 20, 12)  # index, id, folder/name, status
    header = f"{'#':>{widths[0]}}  {'ID':{widths[1]}}  {'Folder/Name':{widths[2]}}  {'Status':{widths[3]}}"
    print(header)
    print('-' * (sum(widths) + 8))
    for idx, (pid, info) in enumerate(profiles):
        name = info.get('name') or info.get('title') or ''
        folder = info.get('folder') or ''
        label = name or folder or ''
        status = info.get('status') or ''
        pid_short = pid if len(pid) <= widths[1] else pid[:widths[1]-3] + '...'
        label_short = label if len(label) <= widths[2] else label[:widths[2]-3] + '...'
        print(f"{idx:>{widths[0]}}  {pid_short:{widths[1]}}  {label_short:{widths[2]}}  {status:{widths[3]}}")


def open_profile_browser(profile_id, profile_info, address, port_from_settings_browser, chrome_driver_path, timeout=5):
    """Inicia el perfil si es necesario, conecta Selenium al puerto de depuración y retorna (driver, debug_port).

    Lanza el perfil vía la API si está en 'Available', usa el puerto si está 'Started'.
    Levanta el WebDriver conectado al puerto remoto y devuelve el `driver` y `debug_port`.
    """
    debug_port = None
    if profile_info.get('status') == 'Available':
        resp = requests.get(f'http://{address}:{port_from_settings_browser}/profile/start/{profile_id}', timeout=timeout)
        resp.raise_for_status()
        debug_port = resp.json().get('data', {}).get('debug_port')
    elif profile_info.get('status') == 'Started':
        debug_port = profile_info.get('debug_port')

    if not debug_port:
        raise RuntimeError('El perfil no expone un puerto de depuración (WebEngine) o no se pudo obtener el puerto.')

    options = Options()
    options.debugger_address = f"{address}:{debug_port}"
    service = Service(chrome_driver_path)
    driver = webdriver.Chrome(service=service, options=options)
    return driver, debug_port


class Undetectable:
    def __init__(self, address=address, port=port_from_settings_browser, chrome_driver_path=chrome_driver_path):
        self.address = address
        self.port = port
        self.chrome_driver_path = chrome_driver_path
        self.profile_id = None
        self.debug_port = None

    def start_driver(self, timeout=5):
        # obtener lista de perfiles
        try:
            resp = requests.get(f'http://{self.address}:{self.port}/list', timeout=timeout)
            resp.raise_for_status()
            list_data = resp.json().get('data', {})
        except Exception as e:
            raise RuntimeError(f"Error al obtener la lista de perfiles: {e}")

        profiles = list(list_data.items())
        if not profiles:
            raise RuntimeError("No hay perfiles disponibles.")

        # mostrar tabla y pedir selección
        print_profiles_table(profiles)
        while True:
            choice = input("Elige el número del perfil a usar (o 'q' para salir): ").strip()
            if choice.lower() in ('q', 'quit', 'exit'):
                raise RuntimeError('Usuario canceló la selección')
            if not choice.isdigit():
                print("Por favor ingresa un número válido.")
                continue
            idx = int(choice)
            if idx < 0 or idx >= len(profiles):
                print("Número fuera de rango.")
                continue
            profile_id, profile_info = profiles[idx]
            if profile_info.get('status') == 'Locked':
                print("Perfil bloqueado. Elige otro perfil.")
                continue
            break

        # iniciar el profile y conectar webdriver
        driver, debug_port = open_profile_browser(profile_id, profile_info, self.address, self.port, self.chrome_driver_path, timeout=timeout)
        self.profile_id = profile_id
        self.debug_port = debug_port
        return driver