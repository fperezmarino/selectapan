odoo.define('integrate_tour_web.package', function(require){
    'use strict';

    var Animation = require('website.content.snippets.animation');
    require('web.dom_ready');
    var ajax = require('web.ajax');
    var odoo = require('web.core');
    var session = require('web.session');
    

    // var _t = core._t;

    // function loadCSS(url) {
    //     var link = document.createElement('link');
    //     link.rel = 'stylesheet';
    //     link.type = 'text/css';
    //     link.href = url;
    //     document.head.appendChild(link);
    // }

    // ajax.loadXML('/integrate_tour_web/views/package_detalle.xml', core.qweb).then(function () {
    //     loadCSS('/integrate_tour_web/static/src/css/detail_style.css');
        
    //     loadCSS('/integrate_tour_web/static/src/css/offers_styles.css');
    //     loadCSS('/integrate_tour_web/static/src/css/offers_responsive.css');
    // });
    

    
    if (window.location.pathname === '/package') {
        miFuncion();
    }

    
   
    $( ".allPrice" ).on('click',function() {

        
        if(this.value != 'initial'){
            miFuncion();
            $("#precioH").val(this.value)
        }
        

      });

      $(".ubica").on('click',function(){
        if(this.value != ''){
            $("#locationH").val(this.value)
            miFuncion();
        }

      })

      $(".hoteles").on('click',function(){
        if(this.value != ''){
            $("#hotelH").val($(this).attr(this.value))
            miFuncion();
        }

      })
      $('#load_more_button').on('click', function() {
        miFuncion(1);
    });
    
    
    function miFuncion(limit = 0) {
        
        let dataseto = {} 
        if($("#precioH").val() != ""){
            dataseto['order']= $("#precioH").val()
        }
        if($("#locationH").val() != ""){
            dataseto['location']= $("#locationH").val()
        }
        if($("#hotelH").val() != ""){
            dataseto['hotel']= $("#hotelH").val()
        }
        console.log(dataseto)

        if(!limit){
           
            dataseto['limit'] = 10; // número de registros por página

        }else{
            dataseto['limit'] = parseInt($("#paginado").val()) 
        }
        

        dataseto['offset'] = 0; // valor inicial del offset
        

        var self = this;
        ajax.jsonRpc('/get_package', 'call', {
            method: 'get',
            args: [dataseto],
        })
        .then(function (data) {
            if(data){
                $("#insert").empty()
                $.each(data, function( index, value ) {
                    console.log(value)
                    
                    var f = new Date().toISOString().split('T')[0]
                    console.log(value.f_d_hasta > f)
                 $("#insert").append(`

                 
                    <div class="col-md-4 ftco-animate fadeInUp ftco-animated">
                        <div class="destination">
                            <a href="/package/${value.id}/" class="img img-2 d-flex justify-content-center align-items-center" style="background-image:url(data:image/png;base64,${value.image});">
                                <div class="icon d-flex justify-content-center align-items-center">
                                    <span class="icon-eye"></span>
                                </div>
                            </a>
                            <div class="text p-3">
                                <div class="d-flex">
                                    <div class="one">
                                        <h3><a href="/package/${value.id}/">${value.name}</a></h3>
                                    </div>
                                    <div class="two">
                                        <span class="price">${value.precio_rate} ${value.currency.symbol}</span>
                                    </div>
                                </div>
                                <div class="d-flex">
                                <div class="one">
                                    <span>Descuento</span>
                                    </br>
                                    <span style="font-size: 10px; color: grey;";>
                                    ${value.descuentos_web && value.f_d_hasta > f? `
                                    Desde ${value.f_d_desde} 
                                    </br>
                                    Hasta ${value.f_d_hasta}
                                    `: ""}
                                    </span>
                                </div>
                                <div class="two">
                                    <span >${value.descuentos_web? value.descuentos_web: ""} %</span>
                                </div>
                                
                            </div>
                                <p class="text_p">${value.reseña}</p>
                                <p class="days">
                                <span>${value.total_days >1? value.total_days+" Dias" : value.total_days+" Dia" }</span>
                                <span>${value.total_night ? value.total_night == 1 ? value.total_night+" Noche"  : value.total_night+" Noches" : ""} </span>
                                
                                </p>
                                
                                <hr/>
                                <p class="bottom-area d-flex">
                                    <span><i class="icon-map-o"></i> ${value.location.name} CA</span> 
                                    <span class="ml-auto"><a href="/package/${value.id}/">Detalles...</a></span>
                                </p>
                        </div>
                    </div>
                
                 `);
                
                 // Actualizar el offset para la próxima página
                
            });

            dataseto.limit += 10;
            $("#paginado").val(dataseto.limit)
            }
        });
    }

    $('.quantity button').on('click', function (e) {
                e.preventDefault();
                var button = $(this);
                var oldValue = button.parent().parent().find('input').val();
                if (button.hasClass('btn-plus')) {
                    var newVal = parseFloat(oldValue) + 1;
                } else {
                    if (oldValue > 0) {
                        var newVal = parseFloat(oldValue) - 1;
                    } else {
                        newVal = 0;
                    }
                }
                button.parent().parent().find('input').val(newVal);
            });
        
        
            $('#abrir_modal_cliente').click(function () {
                $('#modal_primer_form').modal('show');
                if (!session.user_id ) {
                    window.location.href = '/web/login?redirect=/package/' + $('#id_pck_m1').val();
                    return false
                }
            });
        
            $('#modal_cliente_guardar').click(function() {
                Hacerreservacion();
            });
        
            function Hacerreservacion(limit = 0) {
                $("#alertamodaluno").empty();
                
        
                var nombre = $('#nombre_modal').val();
                var cedula_pasaporte = $('#document_modal').val();
                var email = $('#email_modal').val();
                var telefono = $('#telefono_modal').val();
                var fechaalta =$('#fechaalta').val();
                var cantidad = $('#cantidad').val();
                var id_pck_m1 = $('#id_pck_m1').val();
                
        
                if ($('#term_comd')[0].checked) {
                    var term_comd = true
                  } else {
                    var term_comd = false
                  }
                // var term_comd = $("#term_comd").val()
                let yourDate = new Date()
                yourDate.toISOString().split('T')[0]
                if(!nombre){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Nombre Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                            return false
                }
                if(!cedula_pasaporte){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Cedula o pasaporte Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                    return false
                }
                if(!email){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Correo Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                        return false
                }
                if(!fechaalta){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Fecha de reservacion Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                        return false
                }
        
                if(fechaalta >= yourDate){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Fecha de reservacion Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                        return false
                }
                if(!cantidad){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Cantidad Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                        return false
                }
                if(!term_comd){
                    $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            Terminos y condiciones  Es requerido
                            </div>`)
                            setTimeout(function() {
                                $("#alertamodaluno").empty();
                            },3000);
                        return false
                }
        
        
                
                var params = {
                    'nombre': nombre,
                    'cedula_pasaporte': cedula_pasaporte,
                    'email': email,
                    'telefono': telefono,
                    'term_comd':term_comd,
                    'fechaalta':fechaalta,
                    'cantidad':cantidad,
                    'id_pck_m1':id_pck_m1,
                };
                
                
                var url = '/validate_reserva';
                
                ajax.jsonRpc(url, 'call', params).then(function(result) {
                    $("#block_BS").empty();
                    $("#block_usd").empty();
                    if(result.success){
                        $('#modal_primer_form').modal('hide');
                        $('#modal_confirmacion').modal('show');
                        $("#block_BS").append(`
                        <h3>Costos en Bs</h3>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Precio por unidad: <b>${result.data.precio_unidad}Bs</b></li>
                            <li class="list-group-item">Descuento: <b>${result.data.descuento? result.data.descuento: 0}%</b></li>
                            <li class="list-group-item">Total Descuento por unidad: <b>${result.data.descuento? result.data.descuento_unidad:0}Bs</b></li>
                            <li class="list-group-item">Cantida: <b>${result.data.cantidad}</b></li>
                            <li class="list-group-item">Total cantidad sin descuento: <b>${result.data.precio_total_sin_d}Bs</b></li>
                            <li class="list-group-item">Total Descuento Cantidad: <b>${result.data.descuento? result.data.descuento_neto: 0}Bs</b></li>
                            <li class="list-group-item">Total a pagar: <b>${result.data.precio_total_con_d}Bs</b></li>
                        </ul>
                        `)
                        $("#block_usd").append(`
                        <h3>Descripción: </h3>
                        <ul class="list-group list-group-flush">
                            <li class="list-group-item">Precio por unidad: <b>${result.data.precio_unidad_USD}USD</b></li>
                            <li class="list-group-item">Descuento: <b>${result.data.descuento_USD? result.data.descuento_USD: 0}%</b></li>
                            <li class="list-group-item">Total Descuento por unidad: <b>${result.data.descuento_USD? result.data.descuento_unidad_USD: 0}USD</b></li><hr>
                            <li class="list-group-item">Cantida: <b>${result.data.cantidad}</b></li>
                            <li class="list-group-item">Total cantidad sin descuento: <b>${result.data.precio_total_sin_d_USD}USD</b></li>
                            <li class="list-group-item">Total Descuento Cantidad: <b>${result.data.descuento_USD? result.data.descuento_neto_USD:0}USD</b></li>
                            <li class="list-group-item">Total a pagar: <b>${result.data.precio_total_con_d_USD}USD</b></li>
                        </ul>
                        `)
        
        //                 block_BS
        // block_usd
        // modal_cliente_reservar
        
                    }else{
                        $("#alertamodaluno").append(`
                            <div class="alert alert-danger" role="alert">
                            ${result.msj}
                            </div>`)
        
                        setTimeout(function() {
                            $("#alertamodaluno").empty();
                        },3000);
                    }
                    
                 
                
                    
                    
                   
                });
        
            }
        
            $('#modal_cliente_reservar').click(function() {
                reservacion();
            });
        
            function reservacion(){
                var nombre = $('#nombre_modal').val();
                var cedula_pasaporte = $('#document_modal').val();
                var email = $('#email_modal').val();
                var telefono = $('#telefono_modal').val();
                var fechaalta =$('#fechaalta').val();
                var cantidad = $('#cantidad').val();
                var id_pck_m1 = $('#id_pck_m1').val();
        
                var params = {
                    'nombre': nombre,
                    'cedula_pasaporte': cedula_pasaporte,
                    'email': email,
                    'telefono': telefono,
                    'term_comd':term_comd,
                    'fechaalta':fechaalta,
                    'cantidad':cantidad,
                    'id_pck_m1':id_pck_m1,
                };
                
                
                var url = '/Reservar';
                
                ajax.jsonRpc(url, 'call', params).then(function(result) {
                    console.log(result)
        
                    if(result.success){
                        $('#modal_confirmacion').modal('hide');
                        $('#modal_reserva_exitosa').modal('show');
                        
                        setTimeout(function() {
                            $('#modal_reserva_exitosa').modal('hide');
                        },5000);
        
                    }else{
                        $("#alertamodaldos").append(`
                            <div class="alert alert-danger" role="alert">
                            ${result.msj}
                            </div>`)
        
                        setTimeout(function() {
                            $("#alertamodaldos").empty();
                        },3000);
                    }
        
            
            })
        
            }
        
           

   
});

