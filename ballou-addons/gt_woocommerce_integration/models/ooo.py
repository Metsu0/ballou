def updateWoocomProduct(self):
    # update product details,image and variants
    prod_templ_obj = self.env['product.template']
    prdct_obj = self.env['product.product']
    stock_quant_obj = self.env['stock.quant']
    inventry_line_obj = self.env['stock.inventory.line']
    prod_att_obj = self.env['product.attribute']
    prod_attr_vals_obj = self.env['product.attribute.value']
    inventry_line_obj = self.env['stock.inventory.line']
    inventry_obj = self.env['stock.inventory']
    stock_quanty = self.env['stock.quant']


    wcapi = API(url=self.woocommerce_instance_id.location,
                consumer_key=self.woocommerce_instance_id.consumer_key,
                consumer_secret=self.woocommerce_instance_id.secret_key, wp_api=True, version='wc/v2')
    if self.woocommerce_last_update_product_data_date:
        product_data_ids = prod_templ_obj.search(
            [('write_date', '>', self.woocommerce_last_update_product_data_date), ('woocom_id', '!=', False)])
    else:
        product_data_ids = prod_templ_obj.search([('woocom_id', '!=', False)])
    #             product_data_ids = prod_templ_obj.browse([55])
    for each in product_data_ids:
        categs = [{
            "id": each.woo_categ.woocom_id,
        }]
        parent_id = each.woo_categ.parent_id
        while parent_id:
            categs.append({
                "id": parent_id.woocom_id,
            })
            parent_id = parent_id.parent_id
        image_list = []
        count = 1
        for image_data in each.woocom_product_img_ids:
            if image_data.woocom_img_id:
                image_list.append({
                    'id': image_data.woocom_img_id,
                    'src': image_data.url,
                    'position': count
                })
            else:
                image_list.append({
                    'src': image_data.url,
                    'position': count
                })
            count += 1
        prod_vals = {
            'name': str(((each.name).encode('ascii', 'ignore')).decode('utf-8')),
            'sku': str(each.default_code),
            "regular_price": each.woocom_regular_price and str(each.woocom_regular_price) or '0.00',
            'sale_price': each.woocom_price and str(each.woocom_price) or '0.00',
            'weight': str(each.product_wght),
            # str(each.with_context(pricelist=shop.pricelist_id.id).price),
            'dimensions': {
                'width': str(each.product_width),
                'height': str(each.product_hght),
                'length': str(each.product_lngth),

            },
            'description': each.description_sale and str(each.description_sale) or '',
            'short_description': each.description_sale and str(each.description_sale) or '',
            'images': image_list,
            'categories': categs,
            'id': int(each.woocom_id),
        }

        if each.attribute_line_ids:
            p_ids = prdct_obj.search([('product_tmpl_id', '=', each.id)])
            qaunt = 0
            if p_ids:
                stck_quant_id = stock_quanty.search(
                    [('product_id', 'in', p_ids.ids), ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
                for stock in stck_quant_id:
                    qaunt += stock.quantity
            prod_vals.update({
                'type': 'variable',
                'stock_quantity': int(qaunt),
            })
        else:
            p_ids = prdct_obj.search([('product_tmpl_id', '=', each.id)])
            qaunt = 0
            if p_ids:
                stck_quant_id = stock_quanty.search(
                    [('product_id', '=', p_ids[0].id), ('location_id', '=', self.warehouse_id.lot_stock_id.id)])
                for stock in stck_quant_id:
                    qaunt += stock.quantity
            prod_vals.update({
                'type': 'simple',
                'stock_quantity': int(qaunt),
            })
        if prod_vals.get('type') == 'simple':
            prod_url = 'products/' + str(each.woocom_id)
            prd_response = wcapi.post(prod_url, prod_vals)
        attributes = []
        if each.attribute_line_ids:
            attributes = []
            for attr in each.attribute_line_ids:
                values = []
                for attr_value in attr.value_ids:
                    values.append(str(((attr.attribute_id.name).encode('ascii', 'ignore')).decode('utf-8')))
                attributes.append({
                    'id': int(attr.attribute_id.woocom_id),
                    'name': str(((attr.attribute_id.name).encode('ascii', 'ignore')).decode('utf-8')),
                    'options': values,
                    'variation': 'true',
                    'visible': 'false'
                })
            if attributes:
                prod_vals.update({'attributes': attributes})
                prod_url = 'products/' + str(each.woocom_id)
                prod_export_res = wcapi.post(prod_url, prod_vals)

        prod_var_id = prdct_obj.search([('product_tmpl_id', '=', each.id)])

        for var in prod_var_id:
            if not var.product_template_attribute_value_ids:
                continue
            values = []
            for att in var.product_template_attribute_value_ids:
                values.append({
                    'id': att.attribute_id.woocom_id,
                    'option': str(((att.name).encode('ascii', 'ignore')).decode('utf-8')),
                })
            var_vals = {
                'name': str((var.name).encode('ascii', 'ignore')),
                #                     'sale_price': str(var.with_context(pricelist=shop.pricelist_id.id).price),
                'regular_price': var.woocom_regular_price and str(var.woocom_regular_price) or '0.00',
                'sale_price': var.woocom_price and str(var.woocom_price) or '0.00',
                'weight': str(var.product_wght),
                'dimensions': {
                    'width': str(var.product_width),
                    'height': str(var.product_hght),
                    'length': str(var.product_lngth),

                },
                'attributes': values,
            }
            if var.woocom_variant_id:
                var_url = 'products/' + str(each.woocom_id) + '/variations/' + str(var.woocom_variant_id)
            else:
                var_url = 'products/' + str(each.woocom_id) + '/variations'
            prd_response = wcapi.post(var_url, var_vals).json()
            var.write({'woocom_variant_id': prd_response.get('id')})
    return True