from incogniton import IncognitonClient
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import asyncio

class IncognitonDriver:
    def __init__(self):
        self.client = IncognitonClient()
    
    async def get_profiles(self):
        """Obtiene todos los perfiles desde Incogniton"""
        response = await self.client.profile.list()
        return response
    
    async def list_and_select_profile(self):
        """
        Lista todos los perfiles disponibles y permite al usuario seleccionar uno.
        
        Returns:
            IncognitonBrowser: Driver del navegador con el perfil seleccionado
        """
        try:
            # Obtener perfiles
            print("🔍 Fetching Incogniton profiles...")
            response = await self.get_profiles()
            
            # Verificar el estado de la respuesta
            if response.get("status") != "ok":
                print(f"❌ Error fetching profiles: {response}")
                return None
            
            # Extraer la lista de perfiles
            profiles = response.get("profileData", [])
            
            if not profiles or len(profiles) == 0:
                print("❌ No profiles found in Incogniton.")
                return None
            
            # Mostrar lista de perfiles
            print("\n" + "="*70)
            print("Available Incogniton Profiles:")
            print("="*70)
            
            for idx, profile in enumerate(profiles, 1):
                # Extraer información general del perfil
                general_info = profile.get('general_profile_information', {})
                profile_name = general_info.get('profile_name', 'Unnamed Profile')
                browser_id = general_info.get('browser_id', 'N/A')
                profile_notes = general_info.get('profile_notes', '')
                
                # Mostrar información del perfil
                print(f"{idx}. Name: {profile_name}")
                print(f"   ID: {browser_id}")
                if profile_notes:
                    # Mostrar solo la primera línea de las notas si existen
                    first_note = profile_notes.split('\n')[0]
                    print(f"   Notes: {first_note[:50]}{'...' if len(first_note) > 50 else ''}")
                print()
            
            print("="*70)
            
            # Solicitar selección del usuario
            while True:
                try:
                    selection = input(f"\n👉 Select profile number (1-{len(profiles)}) or enter Browser ID: ").strip()
                    
                    # Verificar si es un número (índice de la lista)
                    if selection.isdigit():
                        idx = int(selection)
                        if 1 <= idx <= len(profiles):
                            selected_profile = profiles[idx - 1]
                            break
                        else:
                            print(f"❌ Invalid number. Please enter a number between 1 and {len(profiles)}.")
                    else:
                        # Asumir que es un Browser ID
                        selected_profile = next(
                            (p for p in profiles 
                             if p.get('general_profile_information', {}).get('browser_id') == selection), 
                            None
                        )
                        if selected_profile:
                            break
                        else:
                            print(f"❌ Browser ID '{selection}' not found. Please try again.")
                
                except ValueError:
                    print("❌ Invalid input. Please enter a valid number or Browser ID.")
                except KeyboardInterrupt:
                    print("\n❌ Selection cancelled by user.")
                    return None
            
            # Obtener el Browser ID seleccionado
            general_info = selected_profile.get('general_profile_information', {})
            profile_id = general_info.get('browser_id')
            profile_name = general_info.get('profile_name', 'Unnamed Profile')
            
            print(f"\n✅ Selected profile: {profile_name}")
            print(f"   Browser ID: {profile_id}")
            print("🚀 Starting browser...")
            response = await self.client.automation.launch_selenium(profile_id)
            print("🚀 ~ response:", response)

            if response.get("status") != "ok" or not response.get("url"):
                raise RuntimeError("Invalid Selenium launch response from Incogniton")

            selenium_url = f"http://{response['url']}"

            options = Options()
            options.add_argument("--start-maximized")

            driver = webdriver.Remote(
                command_executor=selenium_url,
                options=options
            )

            print("✅ Browser started successfully!\n")

            return driver
            
        except Exception as e:
            print(f"❌ Error selecting profile: {e} and launching browser.")
            import traceback
            traceback.print_exc()
            raise e
    
    def start_driver(self):
        """
        Método sincrónico para iniciar el driver con selección de perfil.
        Wrapper para usar con código sincrónico.
        
        Returns:
            IncognitonBrowser: Driver del navegador
        """
        return asyncio.run(self.list_and_select_profile())


async def main():
    """Función principal de ejemplo"""
    instance = IncognitonDriver()
    driver = await instance.list_and_select_profile()
    
    if driver:
        print("Browser is ready to use!")
        # Aquí puedes usar el browser para navegar
        driver.get("about:blank")
    else:
        print("Failed to start browser.")


if __name__ == "__main__":
    asyncio.run(main())