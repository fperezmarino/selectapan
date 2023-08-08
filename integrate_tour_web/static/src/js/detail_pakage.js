
// odoo.define('integrate_tour_web.age_discounts', function(require){
//     'use strict';

//     // var $ = require('jquery');
//     require('web.dom_ready');
//     var ajax = require('web.ajax');

   
    
//     $('.quantity button').on('click', function (e) {
//         e.preventDefault();
//         var button = $(this);
//         var oldValue = button.parent().parent().find('input').val();
//         if (button.hasClass('btn-plus')) {
//             var newVal = parseFloat(oldValue) + 1;
//         } else {
//             if (oldValue > 0) {
//                 var newVal = parseFloat(oldValue) - 1;
//             } else {
//                 newVal = 0;
//             }
//         }
//         button.parent().parent().find('input').val(newVal);
//     });


//     $('#abrir_modal_cliente').click(function () {
//         $('#modal_primer_form').modal('show');
//     });

//     $('#modal_cliente_guardar').click(function() {
//         Hacerreservacion();
//     });

//     function Hacerreservacion(limit = 0) {
//         $("#alertamodaluno").empty();
        

//         var nombre = $('#nombre_modal').val();
//         var cedula_pasaporte = $('#document_modal').val();
//         var email = $('#email_modal').val();
//         var telefono = $('#telefono_modal').val();
//         var fechaalta =$('#fechaalta').val();
//         var cantidad = $('#cantidad').val();
//         var id_pck_m1 = $('#id_pck_m1').val();
        

//         if ($('#term_comd')[0].checked) {
//             var term_comd = true
//           } else {
//             var term_comd = false
//           }
//         // var term_comd = $("#term_comd").val()
//         let yourDate = new Date()
//         yourDate.toISOString().split('T')[0]
//         if(!nombre){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Nombre Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//                     return false
//         }
//         if(!cedula_pasaporte){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Cedula o pasaporte Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//             return false
//         }
//         if(!email){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Correo Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//                 return false
//         }
//         if(!fechaalta){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Fecha de reservacion Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//                 return false
//         }

//         if(fechaalta >= yourDate){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Fecha de reservacion Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//                 return false
//         }
//         if(!cantidad){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Cantidad Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//                 return false
//         }
//         if(!term_comd){
//             $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     Terminos y condiciones  Es requerido
//                     </div>`)
//                     setTimeout(function() {
//                         $("#alertamodaluno").empty();
//                     },3000);
//                 return false
//         }


        
//         var params = {
//             'nombre': nombre,
//             'cedula_pasaporte': cedula_pasaporte,
//             'email': email,
//             'telefono': telefono,
//             'term_comd':term_comd,
//             'fechaalta':fechaalta,
//             'cantidad':cantidad,
//             'id_pck_m1':id_pck_m1,
//         };
        
        
//         var url = '/validate_reserva';
        
//         ajax.jsonRpc(url, 'call', params).then(function(result) {
//             $("#block_BS").empty();
//             $("#block_usd").empty();
//             if(result.success){
//                 $('#modal_primer_form').modal('hide');
//                 $('#modal_confirmacion').modal('show');
//                 $("#block_BS").append(`
//                 <h3>Costos en Bs</h3>
//                 <ul class="list-group list-group-flush">
//                     <li class="list-group-item">Precio por unidad: <b>${result.data.precio_unidad}Bs</b></li>
//                     <li class="list-group-item">Descuento: <b>${result.data.descuento? result.data.descuento: 0}%</b></li>
//                     <li class="list-group-item">Total Descuento por unidad: <b>${result.data.descuento? result.data.descuento_unidad:0}Bs</b></li>
//                     <li class="list-group-item">Cantida: <b>${result.data.cantidad}</b></li>
//                     <li class="list-group-item">Total cantidad sin descuento: <b>${result.data.precio_total_sin_d}Bs</b></li>
//                     <li class="list-group-item">Total Descuento Cantidad: <b>${result.data.descuento? result.data.descuento_neto: 0}Bs</b></li>
//                     <li class="list-group-item">Total a pagar: <b>${result.data.precio_total_con_d}Bs</b></li>
//                 </ul>
//                 `)
//                 $("#block_usd").append(`
//                 <h3>Costos en USD</h3>
//                 <ul class="list-group list-group-flush">
//                     <li class="list-group-item">Precio por unidad: <b>${result.data.precio_unidad_USD}USD</b></li>
//                     <li class="list-group-item">Descuento: <b>${result.data.descuento_USD? result.data.descuento_USD: 0}%</b></li>
//                     <li class="list-group-item">Total Descuento por unidad: <b>${result.data.descuento_USD? result.data.descuento_unidad_USD: 0}USD</b></li>
//                     <li class="list-group-item">Cantida: <b>${result.data.cantidad}</b></li>
//                     <li class="list-group-item">Total cantidad sin descuento: <b>${result.data.precio_total_sin_d_USD}USD</b></li>
//                     <li class="list-group-item">Total Descuento Cantidad: <b>${result.data.descuento_USD? result.data.descuento_neto_USD:0}USD</b></li>
//                     <li class="list-group-item">Total a pagar: <b>${result.data.precio_total_con_d_USD}USD</b></li>
//                 </ul>
//                 `)

// //                 block_BS
// // block_usd
// // modal_cliente_reservar

//             }else{
//                 $("#alertamodaluno").append(`
//                     <div class="alert alert-danger" role="alert">
//                     ${result.msj}
//                     </div>`)

//                 setTimeout(function() {
//                     $("#alertamodaluno").empty();
//                 },3000);
//             }
            
         
        
            
            
           
//         });

//     }

//     $('#modal_cliente_reservar').click(function() {
//         reservacion();
//     });

//     function reservacion(){
//         var nombre = $('#nombre_modal').val();
//         var cedula_pasaporte = $('#document_modal').val();
//         var email = $('#email_modal').val();
//         var telefono = $('#telefono_modal').val();
//         var fechaalta =$('#fechaalta').val();
//         var cantidad = $('#cantidad').val();
//         var id_pck_m1 = $('#id_pck_m1').val();

//         var params = {
//             'nombre': nombre,
//             'cedula_pasaporte': cedula_pasaporte,
//             'email': email,
//             'telefono': telefono,
//             'term_comd':term_comd,
//             'fechaalta':fechaalta,
//             'cantidad':cantidad,
//             'id_pck_m1':id_pck_m1,
//         };
        
        
//         var url = '/Reservar';
        
//         ajax.jsonRpc(url, 'call', params).then(function(result) {
//             console.log(result)

//             if(result.success){
//                 $('#modal_confirmacion').modal('hide');
//                 $('#modal_reserva_exitosa').modal('show');
                
//                 setTimeout(function() {
//                     $('#modal_reserva_exitosa').modal('hide');
//                 },5000);

//             }else{
//                 $("#alertamodaldos").append(`
//                     <div class="alert alert-danger" role="alert">
//                     ${result.msj}
//                     </div>`)

//                 setTimeout(function() {
//                     $("#alertamodaldos").empty();
//                 },3000);
//             }

    
//     })

//     }

   

 
// });