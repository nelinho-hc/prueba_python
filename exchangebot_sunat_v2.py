from selenium import webdriver
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.edge.options import Options
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
import time
import os

def inicializar_driver():

    edge_options = Options()
    edge_options.add_argument('--ignore-certificate-errors')
    #edge_options.add_argument('--headless')  # Ejecutar en modo headless (sin interfaz gráfica)
    edge_options.add_argument('--no-sandbox')
    edge_options.add_argument('--disable-dev-shm-usage')
    edge_options.use_chromium = True
    service = EdgeService(EdgeChromiumDriverManager().install())
    driver = webdriver.Edge(service = service, options = edge_options)

    return driver

def extraer_tc_sunat(driver):

    url = "https://e-consulta.sunat.gob.pe/cl-at-ittipcam/tcS01Alias"
    driver.get(url)

    print("\nCargando la página del tipo de cambio - SUNAT.")
    time.sleep(5)
    print("¡Datos extraídos correctamente!")

    html_tc_sunat = driver.page_source
    soup_tc_sunat = BeautifulSoup(html_tc_sunat, 'html.parser')

    return (html_tc_sunat, soup_tc_sunat)

def esAnioBisiesto(anio):

    anio = int(anio)

    if anio % 4 == 0:
        if anio % 100 == 0:
            if anio % 400 == 0:
                anioBisiesto = 1
            else:
                anioBisiesto = 0
        else:
            anioBisiesto = 1
    else:
        anioBisiesto = 0

    return anioBisiesto

def obtener_listaFechas_tc_sunat(html_tc_sunat, soup_tc_sunat, diaHoy):

    # Creación de las listas de los días por cada mes

    diasMes_15 = []
    diasMes_28 = []

    for diaMes_15 in range(1, 16):
        diasMes_15.append(diaMes_15)

    for diaMes_28 in range(16, 29):
        diasMes_28.append(diaMes_28)

    diasMes_29 = diasMes_28.copy()
    diasMes_29.append(29)

    diasMes_30 = diasMes_29.copy()
    diasMes_30.append(30)

    diasMes_31 = diasMes_30.copy()
    diasMes_31.append(31)

    meses_con_30d = ['4', '6', '9', '11']
    meses_con_31d = ['1', '3', '5', '7', '8', '10', '12']
    primeros_dias_meses = ['1', '2', '3', '4', '5', '6', '7', '8', '9']

    tc_compra = []
    tc_venta = []
    lista_fecha_tc = []

    # Ejemplo: Extraer datos de un elemento con un ID específico
    div_calendario = soup_tc_sunat.find(id='holder-calendar')

    # Ejemplo: Extraer datos de un elemento con una clase específica
    clase_tabla = div_calendario.find('table', class_='calendar-table table table-condensed')
    #print(clase_tabla)

    # Encontrar mes y año

    indice_texto = html_tc_sunat.find('table-bordered calendar-day current')
    texto_mes_anio = html_tc_sunat[indice_texto:indice_texto+46]
    #print(texto_mes_anio)

    indice_anio = texto_mes_anio.find('_')
    anio_html = texto_mes_anio[indice_anio+1 : indice_anio+5]
    #print(anio_html)

    indice_mes = texto_mes_anio.find('_', indice_anio+1)
    mes_html = texto_mes_anio[indice_mes+1 : indice_mes+3]
    if '_' in mes_html:
        mes_html = mes_html[0]
    #print(mes_html)

    # Ejemplo: Extraer datos de una división específica (tag <div>)

    if diaHoy <= 15:
        diasAnalizar = diasMes_15.copy()

    elif mes_html in meses_con_30d:
        diasAnalizar = diasMes_30.copy()

    elif mes_html in meses_con_31d:
        diasAnalizar = diasMes_31.copy()

    else:
        AnioBisiesto = esAnioBisiesto(anio_html)

        if AnioBisiesto == 1:
            diasAnalizar = diasMes_29.copy()
        else:
            diasAnalizar = diasMes_28.copy()

    for dia_mes in diasAnalizar:

        dia_mes = str(dia_mes)

        etiqueta_td = 'table-bordered calendar-day current _' + anio_html + '_' + mes_html + '_' + dia_mes + ' js-cal-option'
        #print(etiqueta_td)

        td = clase_tabla.find('td', class_= etiqueta_td)
        #print(td)

        if td is None:
            etiqueta_td = 'table-bordered calendar-day current _' + anio_html + '_' + mes_html + '_' + dia_mes + ' selected js-cal-option'
            td = clase_tabla.find('td', class_= etiqueta_td)
            #print(td)

        if td is None:
            etiqueta_td = 'table-bordered calendar-day current _' + anio_html + '_' + mes_html + '_' + dia_mes + ' c-saturday js-cal-option'
            td = clase_tabla.find('td', class_= etiqueta_td)
            #print(td)

        if td is None:
            etiqueta_td = 'table-bordered calendar-day current _' + anio_html + '_' + mes_html + '_' + dia_mes + ' selected c-saturday js-cal-option'
            td = clase_tabla.find('td', class_= etiqueta_td)
            #print(td)

        if td is None:
            etiqueta_td = 'table-bordered calendar-day current _' + anio_html + '_' + mes_html + '_' + dia_mes + ' c-sunday js-cal-option'
            td = clase_tabla.find('td', class_= etiqueta_td)
            #print(td)

        if td is None:
            etiqueta_td = 'table-bordered calendar-day current _' + anio_html + '_' + mes_html + '_' + dia_mes + ' selected c-sunday js-cal-option'
            td = clase_tabla.find('td', class_= etiqueta_td)
            #print(td)

        if td:

            divs_compra = td.find_all('div', class_='event normal-all-day begin end')
            for div in divs_compra:
                if 'Compra' in div.get_text():
                    valor_compra = div.get_text().split()[-1]  # Extraer el último elemento que es el valor
                    tc_compra.append(valor_compra)

            divs_venta = td.find_all('div', class_='event pap-all-day begin end')
            for div in divs_venta:
                if 'Venta' in div.get_text():
                    valor_venta = div.get_text().split()[-1]  # Extraer el último elemento que es el valor
                    tc_venta.append(valor_venta)

            if dia_mes in primeros_dias_meses:
                dia_fecha_tc = '0' + dia_mes

            else:
                dia_fecha_tc = dia_mes

            if mes_html in primeros_dias_meses:
                mes_fecha_tc = '0' + mes_html

            else:
                mes_fecha_tc = mes_html

            fecha_tc = dia_fecha_tc + '/' + mes_fecha_tc + '/' + anio_html + '|' + valor_compra + '|' + valor_venta
            lista_fecha_tc.append(fecha_tc)

    return (mes_fecha_tc, anio_html, lista_fecha_tc)

def determinar_mes(mes_str):

    if mes_str == '01':
        mes = 'Enero'
    elif mes_str == '02':
        mes = 'Febrero'
    elif mes_str == '03':
        mes = 'Marzo'
    elif mes_str == '04':
        mes = 'Abril'
    elif mes_str == '05':
        mes = 'Mayo'
    elif mes_str == '06':
        mes = 'Junio'
    elif mes_str == '07':
        mes = 'Julio'
    elif mes_str == '08':
        mes = 'Agosto'
    elif mes_str == '09':
        mes = 'Setiembre'
    elif mes_str == '10':
        mes = 'Octubre'
    elif mes_str == '11':
        mes = 'Noviembre'
    elif mes_str == '12':
        mes = 'Diciembre'

    return mes

def main():

    time.sleep(1)
    txt_path = r"E:\Desktop\KPMG\ExchangeBot\SUNAT TC.txt"
    nombre_carpeta_driver = 'edgedriver_win64'
    driver_path = nombre_carpeta_driver + "/msedgedriver.exe"

    try:
        driver = inicializar_driver()
        driver.get("https://www.google.com")

        if driver:
            print("\n¡Genial! El controlador de Edge pudo cargar con éxito la página de Google.")
    
    except:
        print("\nError al cargar el navegador automatizado de Microsoft Edge.\n")

    nombre_txt = os.path.basename(txt_path)
    diaHoy = datetime.today().day

    listaFechas_tc_sunat = []

    (html_tc_sunat, soup_tc_sunat) = extraer_tc_sunat(driver)

    (mes_fecha_tc, anio_html, listaFechas_tc_sunat) = obtener_listaFechas_tc_sunat(html_tc_sunat, soup_tc_sunat, diaHoy)
    mes = determinar_mes(mes_fecha_tc)
    with open(txt_path, 'a') as archivo:
        for elemento in listaFechas_tc_sunat:
            archivo.write("\n" + elemento)
    time.sleep(1)
    print(f"Los datos del tipo de cambio para el mes de {mes} {anio_html} han sido escritos con éxito en el archivo '{nombre_txt}'.")
    driver.quit()

if __name__ == "__main__":
    main()
    time.sleep(2)
    print("\nProceso finalizado. Puede cerrar el programa.\n")
    time.sleep(2)
