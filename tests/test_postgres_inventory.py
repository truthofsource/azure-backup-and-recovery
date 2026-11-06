import importlib.util,pathlib,types,unittest
from unittest.mock import patch
spec=importlib.util.spec_from_file_location('snapshot_cluster',pathlib.Path(__file__).resolve().parents[1]/'scripts/snapshot_cluster.py')
inventory=importlib.util.module_from_spec(spec);spec.loader.exec_module(inventory)
class InventoryBoundaryTests(unittest.TestCase):
    def test_exact_inventory_without_row_values(self):
        results=[types.SimpleNamespace(returncode=0,stdout='portal_plugin\n'),types.SimpleNamespace(returncode=0,stdout='public.jobs|2\npublic.audit|3\n')]
        with patch.object(inventory.subprocess,'run',side_effect=results) as run:
            actual=inventory.snapshot('portal-postgres','restore_admin')
        self.assertEqual(actual['databases'],{'portal_plugin':{'public.jobs':2,'public.audit':3}})
        self.assertTrue(all(isinstance(c.args[0],list) for c in run.call_args_list))
    def test_invalid_target_and_unexpected_database_fail(self):
        with self.assertRaises(ValueError):inventory.snapshot('bad;command','postgres')
        with patch.object(inventory.subprocess,'run',return_value=types.SimpleNamespace(returncode=0,stdout='other_database\n')):
            with self.assertRaises(ValueError):inventory.snapshot('portal-postgres','postgres')
