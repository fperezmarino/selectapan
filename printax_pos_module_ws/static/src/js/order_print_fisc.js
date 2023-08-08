// Impresion de factura fiscal desde lista de ordenes

odoo.define("printax_pos.order_print_fiscal", function(require) 
{
	"use strict";

	var bPar = false;
  
	var Widget = require("web.Widget");
	var rpc = require("web.rpc");
	var cedula = ""
	
	Widget.include(
	{
		events: 
		{
			'click #print_fact_buttone': '_print_fac_fis',
		},
		_print_fac_fis: function(param)
		{
			if(bPar == true)
			{
				bPar = false;
				return;
			}
			bPar = true;
			
			var IdOrder = this.state.data.name;

			rpc.query(
			{
				model: "pos.order",
				method: "printax_print_invoice",
				args: [ 0, 2, IdOrder ,cedula]
			}).then(function(resp) 
				{
					// console.log('order_print_fisc.js - _print_fac_fis - in function');
					
					var bReimpresio = false;
					
					if(resp.tip == "ERR")
					{
						if (resp.err == "Falta la identificación fiscal")
							{
								cedula = prompt(`${resp.err} ingrese el numero de identificación fiscal y vuelva a imprimir factura: `)
								
							}
							if(resp.err == "Falta el nombre del cliente")
							{
								nom = prompt(`${resp.err} ingrese eel nombre  y vuelva a imprimir factura: `)
								
							}
						// console.log('order_print_fisc.js - _print_fac_fis - resp.tip == "ERR"');
						
						alert(resp.err);
						return;
					}
					
					var NameOrder;
					
					if(resp.tip == "COK")
						NameOrder = resp.ord;
					else
						bReimpresio = true;
						
					

					// console.log('order_print_fisc.js - _print_fac_fis comando: ' + comando);

					var xhr = new XMLHttpRequest;
					xhr.open('POST', 'http://localhost:5125/fact', true);
					xhr.setRequestHeader('Content-Type', 'application/json');
					xhr.send(resp.msg);
					
					// console.log('order_print_fisc.js - _print_fac_fis send');

					xhr.onload = function() 
					{
						// console.log('_print_fac_fis - in onload');
						if(xhr.status != 200) 
						{ 
							console.log("Error ${xhr.status}: ${xhr.statusText}");
						} 
						else 
						{ 
							var resp = JSON.parse(xhr.responseText)
							console.log(resp['TIP'] )
							for (const key in resp) {
								if (response_data.hasOwnProperty(key)) {
								  const value = response_data[key];
								  console.log(`Propiedad: ${key}, Valor: ${value}`);
								  // Realiza aquí las acciones que necesites con cada propiedad y valor del objeto
								}
							  }
							
							if(resp['TIP'] == "COK")
							{
								if(bReimpresio == false)
								{
									rpc.query(
									{
										model: "pos.order",
										method: "update_invoice",
										args: [ 0, 
												NameOrder,
												resp['FAC'],
												resp['SER'],
												resp['FEC'],
												resp['VTA'],
												resp['IVA'],
												resp['RPZ'] ]
									}).then(function(resp){});
								}
							}
							else
							{
								alert(resp['err']);
							}
						}
					};	

					xhr.onprogress = function(event) 
					{
						// console.log('_print_fac_fis - in onprogress');
	/*							
						if(event.lengthComputable) 
						{
							console.log(`Received ${event.loaded} of ${event.total} bytes`);
						} 
						else 
						{
							console.log(`Received ${event.loaded} bytes`); // no Content-Length
						}
						
						console.log(xhr.responseText);
	*/
					};

					xhr.onerror = function() 
					{
						console.log("Request failed");
					};
				});
		}
		
	});
	
	return Widget;
});
// clickopenl()







