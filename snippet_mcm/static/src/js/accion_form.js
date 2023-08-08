odoo.define('snippet_mcm.snippet_mcm', function(require){
    'use strict';
    
    
    
    
    
    // var $ = require('jquery');
    require('web.dom_ready');
    var ajax = require('web.ajax');

    $('#enviarsm').on('click', function (e) {
        e.preventDefault();
    
            var nombre = $('#nombresm').val();
            var cedula_pasaporte = $('#cedulasm').val();
            var email = $('#correosm').val();
            var telefono = $('#centrosm').val();

            $( "#block_votante" ).empty();
            // alert('hola')

            var params = {
                'nombre': nombre,
                'cedula_pasaporte': cedula_pasaporte,
                'email': email,
                'telefono': telefono,    
            };
            var url = '/votomsm';
            
            ajax.jsonRpc(url, 'call', params).then(function(result) {
                
                if(result.success){
                    console.log(result.data)

                    $('#modal_confirmacion').modal('show');

                    $("#block_votante").append(`
                    <h2>Datos de votacion</h2>
                    <div class="position-absolute top-50 start-50 translate-middle">${result.data.cedula}</div>
                    <br/>
                    <div class="position-absolute top-50 start-50 translate-middle">${result.data.Nombre}</div>
                    <br/>
                    <div class="position-absolute top-50 start-50 translate-middle">${result.data.estado}</div>
                    <br/>
                    <div class="position-absolute top-50 start-50 translate-middle">${result.data.Municipio}</div>
                    <br/>
                    <div class="position-absolute top-50 start-50 translate-middle">${result.data.centro}</div>
                    <br/>
                    <div class="position-absolute top-50 start-50 translate-middle bg-warning">
                        Se envió a su correo electrónico un link el cual deberá ingresar para continuar con su intención de voto.
                    </div>
                    
                    `)

                    $('#nombresm').val("");
                    $('#cedulasm').val("");
                    $('#correosm').val("");
                    $('#centrosm').val("");

                    

                }
        
        })

        
    });

});