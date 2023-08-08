odoo.define("printax_pos.anular_print_fisc", function (require) {
	"use strict";
  
	var bPar = false;
  
	var Widget = require("web.Widget");
	var rpc = require("web.rpc");
	var cedula = "";
	var nom = "";
  
	function anularFactura(IdOrder) {
	  rpc.query({
		model: "pos.order",
		method: "printax_print_invoice",
		args: [0, 3, IdOrder, cedula, nom],
	  }).then(function (resp) {
		var bReimpresio = false;
  
		if (resp.tip == "ERR") {
		  if (resp.err == "Falta la identificación fiscal") {
			cedula = prompt(
			  `${resp.err} ingrese el numero de identificación fiscal y vuelva a anular factura: `
			);
			// Llamar nuevamente a la función para reintentar la anulación
			anularFactura(IdOrder);
		  }
		  if (resp.err == "Falta el nombre del cliente") {
			nom = prompt(
			  `${resp.err} ingrese el nombre y vuelva a anular factura: `
			);
			// Llamar nuevamente a la función para reintentar la anulación
			anularFactura(IdOrder);
		  }
  
		//   alert(resp.err);
		}else{

			var comando = "https://" + resp.ip + ":" + resp.port;
		var xhr = new XMLHttpRequest;
					

					xhr.open("POST", comando, true);
					xhr.setRequestHeader("Content-Type", "application/json");
					xhr.send(resp.msg);
					
					

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
								
								rpc.query(
								{
									model: "pos.order",
									method: "update_invoice_anulada",
									args: [ 0, 
										IdOrder,
												]
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
  
		
  
		
	  });
	}
  
	Widget.include({
	  events: {
		"click #anu_fact_button": "_anu_fac_fis",
	  },
  
	  _anu_fac_fis: function (param) {
		if (bPar == true) {
		  bPar = false;
		  return;
		}
		bPar = true;
		var IdOrder = this.state.data.name;
  
		// Llamar a la función que maneja la anulación
		anularFactura(IdOrder);
	  },
	});
  
	return Widget;
  });

 // archivo custom_script.js
odoo.define('printax_pos_module_ws.custom_script', function (require) {
    "use strict";
	var Widget = require("web.Widget");
	var rpc = require("web.rpc");


	Widget.include({
		events: {
		  "click #report_x": "_reporte_X",
		  "click #report_z": "_reporte_Z",
		},
	
		_reporte_Z: function (param) {
			var comando = "http://127.0.0.1:5125/rpxz";
			var xhr = new XMLHttpRequest;
			xhr.open("POST", comando, true);
			xhr.setRequestHeader("Content-Type", "application/json");
			xhr.send('Z');
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
						alert('Se imprimió el Reporte Z con éxito.');
						
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
		  
		},
		_reporte_X: function(param){
			var comando = "http://127.0.0.1:5125/rpxz";
			var xhr = new XMLHttpRequest;
			xhr.open("POST", comando, true);
			xhr.setRequestHeader("Content-Type", "application/json");
			xhr.send('X');
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
						alert('Se imprimió el Reporte X con éxito.');
						
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
		
	  });

	  return Widget;
	});





// odoo.define('printax_pos_module_ws.productItemExtension', function(require) {
// 	'use strict';
  
// 	const ProductItem = require('point_of_sale.ProductItem');
// 	const Registries = require('point_of_sale.Registries');
  
// 	// Define una función para mostrar el cuadro de diálogo de manera asincrónica
// 	async function showInputDialog(message) {
// 	  return new Promise((resolve, reject) => {
// 		const input = prompt(message);
// 		resolve(input);
// 	  });
// 	}
  
// 	const CurrencyProductItemFunc = (ProductItem) =>
// 	  class extends ProductItem {
// 		async onProductClick() {
// 		  const selectedProduct = this.props.product.display_name;
  
// 		  if (selectedProduct === 'Genérico SIN IVA' || selectedProduct === 'Genérico con IVA') {
// 			let enteredPrice = await showInputDialog('Ingrese el precio:');
  
// 			// Validar si el usuario ingresó un número válido
// 			while (isNaN(parseFloat(enteredPrice))) {
// 			  alert('Ingrese un número válido.');
// 			  enteredPrice = await showInputDialog('Ingrese el precio:');
// 			}
  
// 			if (enteredPrice !== null && enteredPrice !== '') {
// 			  // Convertir la cadena de texto a un número decimal usando parseFloat
// 			  enteredPrice = parseFloat(enteredPrice);
  
// 			  const order = this.env.pos.get_order();
// 			  const product = this.props.product;
// 			  console.log('Precio ingresado:', product, this.props.product.taxes_id);
  
// 			  order.add_product(product, { quantity: 1, price: enteredPrice });
// 			  order.trigger('change', order); // Notificar a la orden sobre el cambio
// 			}
// 		  } else {
// 			// Ejecuta la acción por defecto al hacer clic en un producto (por ejemplo, mostrar la información del producto)
// 			super.onProductClick();
// 		  }
// 		}
// 	  };
  
// 	Registries.Component.extend(ProductItem, CurrencyProductItemFunc);
  
// 	return ProductItem;
//   });
  

odoo.define('printax_pos_module_ws.productItemExtension', function(require) {
	'use strict';
  
	const ProductItem = require('point_of_sale.ProductItem');
	const Registries = require('point_of_sale.Registries');
  
	// Define una función para mostrar el cuadro de diálogo de manera asincrónica
	async function showInputDialog(message) {
	  return new Promise((resolve, reject) => {
		const input = prompt(message);
		resolve(input);
	  });
	}
  
	const CurrencyProductItemFunc = (ProductItem) =>
	  class extends ProductItem {
		async onProductClick() {
		  const selectedProduct = this.props.product.display_name;
  
		  if (selectedProduct === 'Genérico SIN IVA' || selectedProduct === 'Genérico con IVA') {
			let enteredPrice = await showInputDialog('Ingrese el precio:');
  
			// Validar si el usuario ingresó un número válido
			while (isNaN(parseFloat(enteredPrice))) {
			  alert('Ingrese un número válido.');
			  enteredPrice = await showInputDialog('Ingrese el precio:');
			}
  
			if (enteredPrice !== null && enteredPrice !== '') {
			  // Convertir la cadena de texto a un número decimal usando parseFloat
			  enteredPrice = parseFloat(enteredPrice);
  
			  const order = this.env.pos.get_order();
			  const product = this.props.product;
			  console.log('Precio ingresado:', product, product.taxes_id);
  
			  // Obtener el IVA del producto (si tiene impuestos asociados)
			  const tax_id = product.taxes_id[0]; // Suponemos que el producto tiene un único impuesto asociado
			  const tax = this.env.pos.taxes_by_id[tax_id];
			  const iva = tax && tax.amount / 100; // Obtener la tasa de IVA como decimal
  
			  console.log('IVA del producto:', iva);
  
			  // Calcular el precio sin IVA
			  const priceWithoutTax = enteredPrice / (1 + iva);
  
			  // Agregar el producto a la orden con el precio sin IVA
			  order.add_product(product, { quantity: 1, price: priceWithoutTax });
			  order.trigger('change', order); // Notificar a la orden sobre el cambio
			}
		  } else {
			this.trigger('click-product', this.props.product);
		  }
		}
	  };
  
	Registries.Component.extend(ProductItem, CurrencyProductItemFunc);
  
	return ProductItem;
  });
  




  