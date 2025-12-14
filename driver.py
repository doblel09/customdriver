from typing import Protocol
from seleniumbase import sb_cdp
from drivers.undetectable import Undetectable
from drivers.incogniton_driver import IncognitonDriver
from selenium.webdriver.common.by import By
import time
import random
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.actions.pointer_input import PointerInput
from selenium.webdriver.common.actions.action_builder import ActionBuilder
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import asyncio

class CustomDriver:
    def __init__(self, proxy=None, browser_options={"type": "seleniumbase", "mobile_emulation": False}, type_speed=0.0, wait_speed=0.0, typeSlowly=False):
        """
        Inicializa el CustomDriver con las opciones de navegador especificadas.
        
        Args:
            user: Usuario para configuraciones específicas (opcional)
            proxy: Dirección del proxy en formato IP:Puerto (ej: "192.168.1.1:1080")
            url: URL inicial a cargar (default: "about:blank")
            browser_options: Diccionario con configuración del navegador:
                - type: Tipo de navegador ("seleniumbase", "undetectable", "incogniton")
                - mobile_emulation: Si se debe usar emulación móvil (bool)
            type_speed: Velocidad base entre teclas al escribir (en segundos)
            wait_speed: Tiempo de espera adicional entre acciones (en segundos)
            typeSlowly: Si True, escribe carácter por carácter; si False, escribe instantáneamente
            mobileEmulation: Si se debe usar emulación táctil para clics (bool)
        """
        self.type_speed = type_speed
        self.wait_speed = wait_speed
        self.typeSlowly = typeSlowly
        self.mobileEmulation = browser_options.get("mobile_emulation", False)
        self.cdp = False

        match browser_options.get("type", "seleniumbase"):
            case "incogniton":
                instance = IncognitonDriver()
                self.driver = asyncio.run(instance.list_and_select_profile())
            case "undetectable":
                instance = Undetectable()
                self.driver = instance.start_driver()
            case "seleniumbase":
                self.driver = sb_cdp.Chrome(browser="brave", proxy="socks5h://" + proxy if proxy else None)
                self.mobileEmulation = False
                self.cdp = True

    def quit(self):
        """
        Cierra el navegador y finaliza la sesión del driver.
        """
        self.driver.quit()

    def pause(self):
        """
        Pausa la ejecución del script hasta que el usuario presione Enter.
        Útil para debugging o inspección manual del estado del navegador.
        """
        input("Paused. Press Enter to continue...")

    def get(self, url):
        """
        Navega a la URL especificada.
        
        Args:
            url: URL completa a la que navegar (ej: "https://example.com")
        """
        if self.cdp:
            self.driver.open(url)
            return
        self.driver.get(url)
        time.sleep(random.uniform(1.0, 3.0) + self.wait_speed)

    def change_to_new_tab(self):
        """
        Cambia el foco del driver a la última pestaña abierta.
        Útil cuando se abre un enlace en nueva pestaña y necesitas interactuar con ella.
        """
        self.driver.switch_to.window(self.driver.window_handles[-1])
        time.sleep(random.uniform(0.8, 2.0) + self.wait_speed)

    def type(self, element_selector, text, scroll=False, clickOutside=True):
        """
        Escribe texto en un elemento input/textarea.
        
        Args:
            element_selector: Selector CSS o XPath del elemento donde escribir
            text: Texto a escribir en el elemento
            scroll: Si True, hace scroll al elemento antes de escribir (default: False)
            clickOutside: Si True, hace clic fuera del elemento después de escribir (default: True)
        
        Note:
            El comportamiento depende de typeSlowly:
            - Si typeSlowly=True: Escribe carácter por carácter con delays
            - Si typeSlowly=False: Escribe todo el texto instantáneamente
        """
        if not self.typeSlowly:
            self._type_instantly(element_selector, text, scroll, clickOutside)
        else:
            self._type_slowly(element_selector, text, scroll, clickOutside)
    
    def click(self, element_selector, scroll=False, radio=False):
        """
        Hace clic en un elemento.
        
        Args:
            element_selector: Selector CSS o XPath del elemento a clickear
            scroll: Si True, hace scroll al elemento antes de hacer clic (default: False)
            radio: Si True, usa comportamiento especial para radio buttons (default: False)
        
        Note:
            Si mobileEmulation=True, usa eventos táctiles en lugar de clics de mouse.
        """
        if self.mobileEmulation:
            self._touch_element(element_selector, scroll, radio)
        else:
            self._clickAndWait(element_selector)

    def _clickAndWait(self, element_selector, max_retries=3, retry_delay=4):
        """
        Hace clic en un elemento y espera, con reintentos.
        
        Args:
            driver: WebDriver instance
            element_selector: CSS selector del elemento
            max_retries: Número máximo de intentos (default: 3)
            retry_delay: Tiempo de espera entre intentos en segundos (default: 4)
        
        Raises:
            Exception: Si todos los intentos fallan
        """
        if self.cdp:
            self.driver.click(element_selector)
            time.sleep(random.uniform(0.4, 1.6) + self.wait_speed)
            return

        last_exception = None
        
        for attempt in range(max_retries):
            try:
                time.sleep(random.uniform(0.3, 1.4))            
                # Esperar que el elemento sea clickeable
                button = self.wait_for_clickable_element(element_selector)
                ActionChains(self.driver).move_to_element(button).click().perform()
                time.sleep(random.uniform(0.3, 1.6) + self.wait_speed)
                return  # Éxito - salir de la función
                
            except Exception as e:
                last_exception = e            
                if attempt < max_retries - 1:  # Si no es el último intento
                    time.sleep(retry_delay)
                else:
                    print(f"🔥 All {max_retries} attempts failed for {element_selector}")
        
        # Si llegamos aquí, todos los intentos fallaron
        raise Exception(f"Failed to click element {element_selector} after {max_retries} attempts. Last error: {last_exception}")
    
    def wait_for_clickable_element(self, element_selector, timeout=20, by=By.CSS_SELECTOR):
        """
        Espera hasta que un elemento sea clickeable (visible y habilitado).
        
        Args:
            element_selector: Selector CSS o XPath del elemento
            timeout: Tiempo máximo de espera en segundos (default: 20)
            by: Tipo de selector (By.CSS_SELECTOR, By.XPATH, etc.) (default: By.CSS_SELECTOR)
        
        Returns:
            WebElement: El elemento cuando está listo para ser clickeado
        
        Raises:
            Exception: Si el elemento no se vuelve clickeable dentro del timeout
        """
        try:
            if self.cdp:
                element = self.driver.find_element(element_selector, timeout=timeout)
                time.sleep(random.uniform(0.8, 1.6))
                return element
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.element_to_be_clickable((by, element_selector)))
        except Exception as e:
            raise Exception(f"Error waiting for clickable element {element_selector}: {e}")

    def _type_instantly(self, element_selector, text, scroll=False, clickOutside=True):
        try:
            element = self._find(element_selector)
            if scroll:
                self.scroll_to_element(element_selector if not self.cdp else element)
            if not self.cdp and not self.mobileEmulation:
                ActionChains(self.driver).click(element).perform()

            element.send_keys(text)
            time.sleep(random.uniform(0.3, 2.0))

            if clickOutside and not self.cdp and not self.mobileEmulation:
                body = self.driver.find_element(By.TAG_NAME, "body")
                ActionChains(self.driver).move_to_element(body).click().perform()
        except Exception as e:
            raise Exception(f"Error typing {element_selector}: {e}")
        
    def _type_slowly(self, element_selector, text, scroll=False, clickOutside=True):
        try:
            element = self._find(element_selector)
            
            if (scroll):
                self.scroll_to_element(element_selector)

            if not self.cdp and not self.mobileEmulation:
                ActionChains(self.driver).click(element).perform()

            for char in text:
                element.send_keys(char)
                # type_speed es ahora un multiplicador de la velocidad base
                # type_speed = 0 -> velocidad base (0.3-1.0s)
                # type_speed = 1 -> 2x más lento (0.6-2.0s)
                # type_speed = 2 -> 3x más lento (0.9-3.0s)
                base_min = 0.1
                base_max = 0.5
                multiplier = 1.0 if self.type_speed == 0.0 else (1.0 + self.type_speed)
                delay = random.uniform(base_min * multiplier, base_max * multiplier)
                time.sleep(delay)
            time.sleep(random.uniform(0.8, 2.0))

            if clickOutside and not self.cdp and not self.mobileEmulation:
                body = self.driver.find_element(By.TAG_NAME, "body")
                ActionChains(self.driver).move_to_element(body).click().perform()
        except Exception as e:
            raise Exception(f"Error typing {element_selector}: {e}")
        
    def _touch_element(self, element_selector, scroll=False, radio=False):
        try:
            if self.cdp:
                el = element_selector if type(element_selector) != str else self.driver.find_element(element_selector)
                if scroll:
                    el.scroll_into_view()
                    time.sleep(random.uniform(0.5, 1.6))
                
                if radio:
                    self.driver.click(element_selector) if type(element_selector) == str else None
                    return
                
                el.click()
                time.sleep(random.uniform(0.4, 1.0))
                return
            else:
                el = self._find(element_selector)

            touch = PointerInput("touch", "touch")
            actions = ActionBuilder(self.driver, mouse=touch)

            # 3. Mover a elemento
            actions.pointer_action.move_to(el)

            # 4. Hacer pointer down, pause opcional, pointer up
            actions.pointer_action.pointer_down()
            actions.pointer_action.pause(0.1)
            actions.pointer_action.pointer_up()

            # 5. Ejecutar
            actions.perform()

        except Exception as e:
            raise Exception(f"Error touching element {element_selector}: {e}")
        
    def _find(self, selector,):
        if self.cdp:
            return self.driver.find_element(selector)
        if selector.strip().startswith("//"):
            return self.driver.find_element(By.XPATH, selector)
        else:
            return self.driver.find_element(By.CSS_SELECTOR, selector)
        
    def select_option_by_value(self, element_selector, value):
        """
        Selecciona una opción en un elemento <select> dropdown por su valor.
        
        Args:
            element_selector: Selector CSS o XPath del elemento <select>
            value: Valor del atributo 'value' de la opción a seleccionar
        
        Example:
            driver.select_option_by_value("#country", "US")
            # Selecciona <option value="US">United States</option>
        """
        try:
            if self.cdp:
                self.driver.select_option_by_value(element_selector, value)
                time.sleep(random.uniform(0.3, 1.2))
                return
            element = self._find(element_selector)
            select = Select(element)
            select.select_by_value(value)
            
            # self.driver.execute_script("""
            #     arguments[0].dispatchEvent(new Event('change', { bubbles: true }));
            #     arguments[0].dispatchEvent(new Event('input', { bubbles: true }));
            # """, element)
            time.sleep(random.uniform(0.6, 1.8))
        except Exception as e:
            print(f"Error selecting option: {e}")
        
    def wait_for_visible_element(self, element_selector, timeout=20, by=By.CSS_SELECTOR):
        """
        Espera hasta que un elemento sea visible en la página.
        
        Args:
            element_selector: Selector CSS o XPath del elemento
            timeout: Tiempo máximo de espera en segundos (default: 20)
            by: Tipo de selector (By.CSS_SELECTOR, By.XPATH, etc.) (default: By.CSS_SELECTOR)
        
        Returns:
            WebElement: El elemento cuando es visible
        
        Raises:
            Exception: Si el elemento no se vuelve visible dentro del timeout
        """
        try:
            if self.cdp:
                element = self.driver.find_element(element_selector, timeout=timeout)
                time.sleep(random.uniform(0.8, 1.6))
                return element
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.visibility_of_element_located((by, element_selector)))
        except Exception as e:
            raise Exception(f"Error waiting for element {element_selector}: {e}")
        
    def scroll_to_element(self, element):
        """
        Hace scroll suave hasta que un elemento sea visible en el viewport.
        
        Args:
            element: Puede ser un WebElement o un string con el selector CSS/XPath
        
        Returns:
            WebElement: El elemento al que se hizo scroll
        
        Raises:
            Exception: Si hay un error al hacer scroll
        """
        try:
            is_selector = True if type(element) == str else False
            el = self._find(element) if is_selector else element
            if self.cdp:
                el.scroll_into_view()
            else:
                self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth'})", el)
            time.sleep(random.uniform(0.5, 1.6))
            return el
        except Exception as e:
            raise Exception(f"Error scrolling to element {el}: {e}")
        
    def getElement(self, element_selector, timeout=20, by=By.CSS_SELECTOR):
        """
        Obtiene un elemento del DOM esperando a que esté presente.
        
        Args:
            element_selector: Selector CSS o XPath del elemento
            timeout: Tiempo máximo de espera en segundos (default: 20)
            by: Tipo de selector (By.CSS_SELECTOR, By.XPATH, etc.) (default: By.CSS_SELECTOR)
        
        Returns:
            WebElement: El elemento encontrado
        
        Raises:
            Exception: Si el elemento no se encuentra dentro del timeout
        
        Note:
            Este método solo verifica que el elemento exista en el DOM,
            no garantiza que sea visible o clickeable.
        """
        try:
            if self.cdp:
                return self.driver.find_element(element_selector, timeout=timeout)
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.presence_of_element_located((by, element_selector)))
            return self.driver.find_element(by, element_selector)
        except Exception:
            raise Exception(f"Error getting element {element_selector}")
        
    def get_current_url(self):
        """
        Obtiene la URL actual del navegador.
        
        Returns:
            str: URL completa de la página actual
        
        Example:
            url = driver.get_current_url()
            print(url)  # "https://example.com/page"
        """
        if self.cdp:
            return self.driver.get_current_url()
        return self.driver.current_url
    
    def wait_for_element_to_disappear(self, element_selector, timeout=20, by=By.CSS_SELECTOR):
        """
        Espera hasta que un elemento desaparezca del DOM o se vuelva invisible.
        
        Args:
            element_selector: Selector CSS o XPath del elemento
            timeout: Tiempo máximo de espera en segundos (default: 20)
            by: Tipo de selector (By.CSS_SELECTOR, By.XPATH, etc.) (default: By.CSS_SELECTOR)
        """
        try:
            if self.cdp:
                return
            wait = WebDriverWait(self.driver, timeout)
            wait.until(EC.invisibility_of_element_located((by, element_selector)))
        except Exception as e:
            raise Exception(f"Error waiting for element {element_selector} to disappear: {e}")
    
class DriverMethods(Protocol):
    def get(self, url: str) -> None: ...
    def quit(self) -> None: ...
    def change_to_new_tab(self) -> None: ...
    def type(self, element_selector: str, text: str, scroll: bool = False, clickOutside: bool = True) -> None: ...
    def click(self, element_selector: str, scroll: bool = False, radio: bool = False) -> None: ...
    def select_option_by_value(self, element_selector: str, value: str) -> None: ...
    def wait_for_visible_element(self, element_selector: str, timeout: int = 20, by=By.CSS_SELECTOR) -> any: ...
    def get_current_url(self) -> str: ...
    def getElement(self, element_selector: str, timeout: int = 20, by=By.CSS_SELECTOR) -> any: ...
    def scroll_to_element(self, element: any) -> any: ...
    def wait_for_clickable_element(self, element_selector: str, timeout: int = 20, by=By.CSS_SELECTOR) -> any: ...
    def wait_for_element_to_disappear(self, element_selector: str, timeout: int = 20, by=By.CSS_SELECTOR) -> None: ...
    mobileEmulation: bool