# Copyright 2025 Opener B.V.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class ResGroups(models.Model):
    _inherit = "res.groups"

    included_menu_ids = fields.Many2many(
        comodel_name="ir.ui.menu",
        compute="_compute_included_menu_ids",
        readonly=False,
        recursive=True,
        store=True,
        relation="ir_ui_menu_included_group_rel",
        column1="gid",
        column2="menu_id",
        string="Strict Menu Access",
        help=(
            "If set, users in this group have access to *only* this menu. You "
            "can use it to drastically limit the GUI access that users in this "
            "group have. If a user is in more than one group with strict menu "
            "access, they will have access to all the menus linked to all their "
            "groups."
        ),
    )

    @api.depends("included_menu_ids.parent_id")
    def _compute_included_menu_ids(self):
        """Add parents when menu is updated"""

        def add_parents(menu, menus):
            if not menu.parent_id or menu.parent_id in menus:
                return menus
            return add_parents(menu.parent_id, menus + menu.parent_id)

        for group in self.filtered("included_menu_ids"):
            menus = group.included_menu_ids
            for menu in menus:
                menus = add_parents(menu, menus)
            group.included_menu_ids = menus

    @api.model_create_multi
    def create(self, vals_list):
        """Add any parent menus of included menus"""
        res = super().create(vals_list)
        res.with_context(included_menu_ids_add_parents=True)
        return res

    def write(self, vals):
        """Add any parent menus of included menus"""
        res = super().write(vals)
        if "included_menu_ids" in vals and not self.env.context.get(
            "included_menu_ids_add_parents"
        ):
            self.with_context(
                included_menu_ids_add_parents=True
            )._compute_included_menu_ids()
        return res
