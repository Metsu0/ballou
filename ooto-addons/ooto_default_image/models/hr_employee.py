# -*- coding: utf-8 -*-

import base64
from io import BytesIO
from random import randint

from PIL import Image, ImageDraw, ImageFont

from odoo import models, http, fields, api

color_background = [
    (252, 52, 113),
    (216, 27, 96),
    (173, 20, 87),
    (156, 39, 176),
    (103, 58, 183),
    (63, 81, 181),
    (33, 150, 243),
    (3, 169, 244),
    (0, 188, 212),
    (77, 182, 172),
    (0, 150, 136),
    (76, 175, 80),
    (139, 195, 74),
    (192, 202, 51),
    (251, 192, 45),
    (255, 160, 0),
    (245, 124, 0),
    (255, 87, 34),
    (244, 67, 54),
    (207, 125, 85),
    (121, 85, 72),
    (74, 74, 74),
    (158, 158, 158),
    (144, 164, 174),
    (96, 125, 139),
    (69, 90, 100),
]


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    image_1920 = fields.Image(default=False)

    def create_image(self, name):
        img = Image.new('RGB', (125, 125), color=color_background[randint(0, len(color_background) - 1)])
        addons_path = http.addons_manifest['ooto_default_image']['addons_path']
        fnt = ImageFont.truetype(addons_path + '/ooto_default_image/static/src/fonts/Nunito-Bold.ttf', 55)
        d = ImageDraw.Draw(img)
        n = name.split(' ')
        if len(n) > 1:
            initial = "".join([n[0][:1].upper(), n[1][:1].upper()])
        else:
            initial = name[:2].upper()
        w, h = d.textsize(initial.upper(), font=fnt)
        d.text(((125 - w) / 2, (100 - h) / 2), initial.upper(), font=fnt, fill=(255, 255, 255))
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue())

    @api.model
    def create(self, values):
        if not values.get('image_1920', False):
            partner_obj = self.env['res.partner']
            name_order = partner_obj._get_names_order()
            if values.get('lastname', False) and values.get('firstname', False):
                if name_order == 'first_last':
                    name = "%s %s" % (values.get('firstname'), values.get('lastname'))
                else:
                    name = "%s %s" % (values.get('lastname'), values.get('firstname'))
            else:
                name = values.get('name', False)
            image_binary = self.create_image(name.strip())
            values.update({'image_1920': image_binary})
        return super(HrEmployee, self).create(values)

    def write(self, values):
        for rec in self:
            if not values.get('image_1920', rec.image_1920):
                image_binary = self.create_image(rec.name)
                values.update({'image_1920': image_binary})
        return super(HrEmployee, self).write(values)
