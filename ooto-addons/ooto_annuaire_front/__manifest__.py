# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2019 eTech Consulting (<http://www.etechconsulting-mg.com>). All Rights Reserved
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': 'OOTO - Annuaire Front',
    'version': '13.0.1.0.0',
    'category': 'Site Web',
    'sequence': -12,
    'summary': 'OOTO - Annuaire Front',
    'description': """ OOTO - Annuaire Front """,

    'author': 'eTech Consulting',
    'website': 'http://www.etechconsulting-mg.com',

    'depends': ['base', 'website', 'ooto_annuaire', 'web', 'ooto_base', 'ooto_hr_account'],
    'data': [
        "views/assets.xml",
        "data/data.xml",
        "views/annuaire_templates.xml",
        "views/templates.xml",
    ],
    'qweb': [],
    'demo': [],
    'installable': True,
    'application': False,
}
