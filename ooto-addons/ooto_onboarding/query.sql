UPDATE ir_model_data SET noupdate=false WHERE name='stage_draft' AND module='survey';
UPDATE ir_model_data SET noupdate=false WHERE name='stage_in_progress' AND module='survey';
UPDATE ir_model_data SET noupdate=false WHERE name='stage_closed' AND module='survey';
UPDATE ir_model_data SET noupdate=false WHERE name='stage_permanent' AND module='survey';