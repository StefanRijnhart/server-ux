# Copyright 2020 Tecnativa - Víctor Martínez
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase


class TestIrUiMenuCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_admin = cls.env.ref("base.user_admin").id
        cls.group_hide_menu = cls.env["res.groups"].create(
            {"name": "Hide menu items custom", "users": [(4, cls.user_admin)]}
        )
        cls.model_ir_ui_menu = cls.env["ir.ui.menu"]
        cls.menu1 = cls.env.ref("base.menu_management")
        cls.menu2 = cls.env.ref("base.menu_action_res_users")
        cls.menu3 = cls.menu2.copy()

    def test_ir_ui_menu_admin(self):
        items = self.model_ir_ui_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertIn(self.menu1.id, items)
        self.assertIn(self.menu2.id, items)
        self.assertIn(self.menu3.id, items)
        # Update ir_ui_menu to assign excluded_group_ids
        self.menu1.write({"excluded_group_ids": [(4, self.group_hide_menu.id)]})
        items = self.model_ir_ui_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertNotIn(self.menu1.id, items)
        self.assertIn(self.menu2.id, items)
        self.assertIn(self.menu3.id, items)

        # Now restrict the group to a single menu
        self.group_hide_menu.included_menu_ids = self.menu2
        # The parent structure is added automatically
        self.assertIn(self.menu2.parent_id, self.group_hide_menu.included_menu_ids)
        self.assertIn(
            self.menu2.parent_id.parent_id, self.group_hide_menu.included_menu_ids
        )
        # Access is now restricted to the configured menu + its parent
        items = self.model_ir_ui_menu.with_user(self.user_admin)._visible_menu_ids()
        self.assertEqual(
            set(items),
            {
                self.menu2.parent_id.parent_id.id,
                self.menu2.parent_id.id,
                self.menu2.id,
            },
        )
