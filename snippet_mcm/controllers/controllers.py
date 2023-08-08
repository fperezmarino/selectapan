# -*- coding: utf-8 -*-
from odoo import http
import requests
from odoo.http import request, Response
from bs4 import BeautifulSoup


class SnippetMcm(http.Controller):

    @http.route('/votomsm', type='json', auth='public')
    def Reserva(self, **post):

        
        
        cedula = post.get('cedula_pasaporte')
        # nombre = post.get('nombre')
        # email = post.get('email')
        # telefono = post.get('telefono')
        # term_comd = post.get('term_comd')
        # cantidad = int(post.get('cantidad'))

        url_semilla = "http://www.cne.gob.ve/web/registro_electoral/ce.php?"

        nacionalidad = 'V'
        
        url_compuesta = url_semilla + 'nacionalidad=' + \
            nacionalidad + '&' + 'cedula=' + cedula
        requestsr = requests.get(url_compuesta)
        soup = BeautifulSoup(requestsr.content, "html.parser")
        if requestsr.status_code == 200:
            contenList = []
            
            # 10:24 los <td> del árbol que nos interesa
            for contenido in soup.find_all('td')[10: 24]:
                dato = contenido.text
                contenList.append(dato.strip())

            datos = {
                'cedula' : contenList[1],
                'Nombre' : contenList[3],
                'estado'  : contenList[5],
                'Municipio' : contenList[7],
                'centro' : contenList[11],

            }
            print(datos)
            return {'success': True, 'data' : datos}
        else:
            return {'success': False, 'data' : requestsr.status_code}
