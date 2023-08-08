// Modulo de impresión de factura fiscal para punto de venta 
// Versión 1.0.0 - 2020.09.11 - Hernán Navarro
// Versión 1.2.0 - 2022.07.15 - Adaptatación a Odoo 15

odoo.define('printax_pos_module_ws.ReceiptScreenButton', function(require)
{
	"use strict";

	const Registries = require('point_of_sale.Registries');
	const ReceiptScreen = require('point_of_sale.ReceiptScreen');
	var rpc = require('web.rpc');
	var cedula = ""
	var nom = ""

	const CustomButtonReceiptScreen = (ReceiptScreen) =>
		class extends ReceiptScreen
		{
			constructor()
			{
				super(...arguments);
			}

			OnPrintFactFiscal()
			{
				var IdOrder = this.env.pos.get_order().uid;
				rpc.query(
				{
					model: 'pos.order',
					method: 'printax_print_invoice',
					args: [ 0, 1, IdOrder, cedula,nom ]
				}).then(function(resp)
					{
						if(resp.tip == "COK")
						{
							var NameOrder = resp.ord;
							var xhr = new XMLHttpRequest;
							xhr.open('POST', 'http://localhost:5125/fact', true);
							xhr.setRequestHeader('Content-Type', 'application/json');
							xhr.send(resp.msg);

							xhr.onload = function()
							{
								if(xhr.status != 200)
								{
									console.log('Error ${xhr.status}: ${xhr.statusText}');
								}
								else
								{
									var resp = JSON.parse(xhr.responseText)

									console.log(resp.TIP)
									

									if(resp.TIP == "COK")
									{
										rpc.query(
										{
											model: 'pos.order',
											method: 'update_invoice',
											args: [ 0,
													NameOrder,
													resp.FAC,
													resp.SER,
													resp.FEC,
													resp.VTA,
													resp.IVA,
													resp.RPZ ]
										}).then(function(resp){});
									}
									else
									{
										alert(resp['err']);
									}
								}
							};

							xhr.onprogress = function(event)
							{
							};

							xhr.onerror = function()
							{
								console.log("Request failed");
							};
						}
						else
						{
							if (resp.err == "Falta la identificación fiscal")
							{
								cedula = prompt(`${resp.err} ingrese el numero de identificación fiscal y vuelva a imprimir factura: `)
								
							}
							if(resp.err == "Falta el nombre del cliente")
							{
								nom = prompt(`${resp.err} ingrese eel nombre  y vuelva a imprimir factura: `)
								
							}
							// alert(resp.err);

						}
					});
			}
		};

	Registries.Component.extend(ReceiptScreen, CustomButtonReceiptScreen);
	return CustomButtonReceiptScreen;
});

odoo.define("printax_pos.open_drawer2", function(require) 
{
	"use strict";
	const PaymentScreen = require('point_of_sale.ReceiptScreen');
    const Registries = require('point_of_sale.Registries');

    const PosHrpPaymentScreen = (PaymentScreen_) =>
          class extends PaymentScreen_ {
			constructor()
			{
				super(...arguments);
			}
			clickopen() 
			{

			var comando = "http://127.0.0.1:5125/drawer";
			var xhr = new XMLHttpRequest;
			xhr.open("POST", comando, true);
			xhr.setRequestHeader("Content-Type", "application/json");
			xhr.send('open');
			xhr.onload = function() 
			{
				if(xhr.status != 200) 
				{ 
					console.log("Error ${xhr.status}: ${xhr.statusText}");
				} 
				else 
				{ 
					var resp = JSON.parse(xhr.responseText)
					if(resp['TIP'] == "COK")
					{
						console.log('Se abrioexitosamente.');
						
					}
					else
					{
						alert(resp['err']);
					}
				}
			};	

			xhr.onprogress = function(event) 
			{
				
			};

			xhr.onerror = function() 
			{
				console.log("Request failed");
			}; 
			
			
				
			}
          };

    Registries.Component.extend(PaymentScreen, PosHrpPaymentScreen);

    return PosHrpPaymentScreen;

	
});

odoo.define('printax_pos.ReprintReceiptScreen', function (require) {
    'use strict';

    const AbstractReceiptScreen = require('point_of_sale.AbstractReceiptScreen');
    const Registries = require('point_of_sale.Registries');
	var rpc = require('web.rpc');

    const ReprintReceiptScreentt = (AbstractReceiptScreen) => 
		class extends AbstractReceiptScreen
		{
			constructor()
			{
				super(...arguments);
			}
			tryReprinttu(ev) {
				var IdOrder = ev.target.dataset.orderId;
				
				rpc.query(
					{
						model: 'pos.order',
						method: 'printax_reprint_invoice',
						args: [ 0, 1, IdOrder,]
					}).then(function(resp)
						{
							if(resp.tip == "COK" || resp.tip == "ROK" )
							{
								var NameOrder = resp.ord;
								var xhr = new XMLHttpRequest;
								xhr.open('POST', `http://localhost:5125/${resp.tip == "COK"? "fact" : "rpfact"}`, true);
								xhr.setRequestHeader('Content-Type', 'application/json');
								xhr.send(resp.msg);

								xhr.onload = function()
								{
									if(xhr.status != 200)
									{
										console.log('Error ${xhr.status}: ${xhr.statusText}');
									}
									else
									{
										var resp = JSON.parse(xhr.responseText)

										console.log(resp)
										

										if(resp.TIP == "COK")
										{
											rpc.query(
											{
												model: 'pos.order',
												method: 'update_invoice',
												args: [ 0,
														NameOrder,
														resp.FAC,
														resp.SER,
														resp.FEC,
														resp.VTA,
														resp.IVA,
														resp.RPZ ]
											}).then(function(resp){
												
											});
										}
										
										else
										{
											alert(resp['err']);
										}
									}
								};

								xhr.onprogress = function(event)
								{
								};

								xhr.onerror = function()
								{
									console.log("Request failed");
								};
							}
							else
							{
								if (resp.err == "Falta la identificación fiscal")
								{
									cedula = prompt(`${resp.err} ingrese el numero de identificación fiscal y vuelva a imprimir factura: `)
									
								}
								if(resp.err == "Falta el nombre del cliente")
								{
									nom = prompt(`${resp.err} ingrese eel nombre  y vuelva a imprimir factura: `)
									
								}
								// alert(resp.err);

							}
						});
			}
		}
        
        
    
    Registries.Component.extend(AbstractReceiptScreen, ReprintReceiptScreentt);
	return ReprintReceiptScreentt;
    
});
