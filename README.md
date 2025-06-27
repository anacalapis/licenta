## Automatizarea scorului și creșterea preciziei timpului de joc la baschet

<br>

## Adresa repository-ului
https://github.com/anacalapis/licenta 

## Explicarea fiecărui fișier din repository
**Fișiere ce sunt încărcate pe diferitele dispozitive din cadrul machetei:**
| Numele fișierului         | Unde este încărcat codul                                               |
| :------------------------:|:----------------------------------------------------------------------:|
| arduino_control_timer     | pe placa Arudino                                                       |
| esp_inel_senzor           | pe microcontroler-ul ESP32 ce este poziționat la inelul 1              |
| esp_inel2_senzor          | pe microcontroler-ul ESP32 ce este poziționat la inelul 2              |
| imu                       | pe microcontroler-ul ESP32 ce este introdus în minge                   |
| esp_starea_butoanelor     | pe microcontroler-ul ESP32 ce se află la dispoziția arbitrului         |

<br>

**Alte fișiere folosite pe parcursul proiectului:**
| Numele fișierului         | La ce a fost folosit                                                               |
| :------------------------:|:----------------------------------------------------------------------------------:|
| find_MAC_address_for_ESP  | pentru găsirea adresei MAC a dispozitivului, necesară la conectarea prin Bluetooth |

<br>

**Fișiere ce trebuie lansate în execuție pe Raspberry Pi:**
| Numele fișierului         | Care este rolul lui                                                                          |
| :------------------------:|:--------------------------------------------------------------------------------------------:|
| camera.py                 | să scrie în fișier distanțele mingii față de cele două panouri                               |
| program_principal.py      | lansarea în paralel a mai multor funcții, pentru sincronizarea execuției programului         |

## Crearea mediului de lucru
* Datorită faptului că cele două fișiere sunt scrise în Python, avem nevoie, prima dată, de instalarea acestuia.
    * `sudo apt install python3` - se instalează Python 3
* Pentru a nu avea probleme, se recomandă crearea și utilizarea unui mediu virtual:
    * `sudo apt install python3-venv` - instalare necesară pentru a putea crea un mediu virtual
    * `python -m venv nume` - se crează mediul virtual, unde *nume* reprezintă numele acestuia
    * `source nume/bin/activate` - se accesează mediul virtual
    * `deactivate` - dezactivarea mediului virtual
* Instalarea protocolului de comunicare Bluetooth 
    * `sudo apt-get install libbluetooth-dev` - se instalează pachetul pentru aplicații ce utilizează Bluetooth, în afara mediului de lucru
    * `pip install pybluez` - bibliotecă Python pentru comunicarea Bluetooth, se rulează în interiorul mediului virtual
* Instalarea bibliotecilor necesare pentru partea de procesare a imaginilor
    * `pip install depthai` - pentru capturarea, procesarea și filtrarea imaginilor
    * `pip install opencv-python` - pentru detecția obiectului
    * `pip install numpy` - pentru diferite calcule numerice

## Lansarea în execuție a celor două programe .py
Se intră în mediul virtual conform comenzilor de mai sus și se deschid două terminale. 
* În primul, se va rula comanda `python camera.py`. Se va deschide camera video și se va aștepta selectarea obiectului. Pentru a închide programul, se va apăsa tasta `q`.
* În cel de-al doilea, se va rula comanda `python program_principal.py`și se așteaptă conectarea celor patru microcontrolere.

