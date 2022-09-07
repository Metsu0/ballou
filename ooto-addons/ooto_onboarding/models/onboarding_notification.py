# -*- coding: utf-8 -*-

from odoo import models, fields,_


class OnboardingNotification(models.Model):
    _name = "onboarding.notification"
    _description = "Onboarding Notification"
    _rec_name = "task_type"

    task_type = fields.Selection([
        ('signature', _('Signature')),
        ('form', _('Form')),
        ('equipment', _('Equipment')),
        ('software', _('Software')),
        ('video', 'Video'),
        ('document', 'Document'),
        ('url', _('External URL')),
        ('internal_url', _('Internal URL')),
        ('document_fill', _('Document to fill')),
        ('upload_file', _('Upload file')),
        ('email', _('Email')),
    ], string="Task type", readonly=True)
    title = fields.Char(string="Title", required=True)
    text = fields.Text(string="Text to display", required=True)


class OnboardingWeeklyNotification(models.Model):
    _name = "onboarding.weekly.notification"
    _description = "Onboarding Weekly Notification"

    name = fields.Char(default="Onboarding Weekly Notification")
    notification_day = fields.Selection([
        ('0', _('Monday')),
        ('1', _('Tuesday')),
        ('2', _('Wednesday')),
        ('3', _('Thursday')),
        ('4', _('Friday')),
        ('5', _('Saturday')),
        ('6', _('Sunday')),
    ], string="Notification Day", required=True)
    title = fields.Char(string="Title", required=True)
    text = fields.Text(string="Text to display", required=True)
    is_active = fields.Boolean(string="Activate", default=False)