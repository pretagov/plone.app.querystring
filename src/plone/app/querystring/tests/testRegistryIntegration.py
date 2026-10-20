from plone.app.querystring.testing import PLONEAPPQUERYSTRING_INTEGRATION_TESTING

import unittest


class TestOperationDefinitions(unittest.TestCase):
    layer = PLONEAPPQUERYSTRING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_string_equality(self):
        registry = self.portal.portal_registry

        prefix = "plone.app.querystring.operation.string.is"
        self.assertTrue(prefix + ".title" in registry)

        self.assertEqual(registry[prefix + ".title"], "Is")
        self.assertEqual(
            registry[prefix + ".description"], "Tip: you can use * to autocomplete."
        )
        self.assertEqual(
            registry[prefix + ".operation"], "plone.app.querystring.queryparser._equal"
        )

    def test_date_lessthan(self):
        registry = self.portal.portal_registry
        prefix = "plone.app.querystring.operation.date.lessThan"

        self.assertTrue(prefix + ".title" in registry)

        self.assertEqual(registry[prefix + ".title"], "Before date")
        self.assertEqual(registry[prefix + ".description"], "Please use YYYY/MM/DD.")
        self.assertEqual(
            registry[prefix + ".operation"],
            "plone.app.querystring.queryparser._dateLessThan",
        )

    def test_string_search(self):
        registry = self.portal.portal_registry
        prefix = "plone.app.querystring.operation.string.search"

        self.assertEqual(registry[prefix + ".title"], "Search")
        self.assertEqual(
            registry[prefix + ".operation"],
            "plone.app.querystring.queryparser._search",
        )
        self.assertIn(
            prefix,
            registry["plone.app.querystring.field.SearchableText.operations"],
        )

    def test_upgrade_15_to_16(self):
        registry = self.portal.portal_registry
        setup = self.portal.portal_setup
        profile = "plone.app.querystring:default"
        operations = "plone.app.querystring.field.SearchableText.operations"
        search = "plone.app.querystring.operation.string.search"
        less_than = "plone.app.querystring.operation.date.lessThan.operation"

        # A site at 15 from upstream (date operators) or from the fork
        # (search operator) gets both from the 15 -> 16 step.
        registry[operations] = [op for op in registry[operations] if op != search]
        registry[less_than] = "plone.app.querystring.queryparser._lessThan"
        setup.setLastVersionForProfile(profile, "15")

        setup.upgradeProfile(profile)

        self.assertEqual(setup.getLastVersionForProfile(profile), ("16",))
        self.assertIn(search, registry[operations])
        self.assertEqual(
            registry[less_than], "plone.app.querystring.queryparser._dateLessThan"
        )


class TestFieldDefinitions(unittest.TestCase):
    layer = PLONEAPPQUERYSTRING_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer["portal"]

    def test_getId(self):
        registry = self.portal.portal_registry
        prefix = "plone.app.querystring.field.getId"
        self.assertTrue(prefix + ".title" in registry)

        self.assertEqual(registry[prefix + ".title"], "Short name (id)")

        operations = registry[prefix + ".operations"]
        self.assertEqual(len(operations), 2)

        equal = "plone.app.querystring.operation.string.is"
        self.assertTrue(equal in operations)

        exclude = "plone.app.querystring.operation.string.isNot"
        self.assertTrue(exclude in operations)

        self.assertEqual(
            registry[prefix + ".description"],
            "The short name of an item (used in the url)",
        )
        self.assertEqual(registry[prefix + ".enabled"], True)
        self.assertEqual(registry[prefix + ".sortable"], True)
        self.assertEqual(registry[prefix + ".group"], "Metadata")

    def test_getobjpositioninparent_largerthan(self):
        """Bug reported as Issue #22

        Names not matching for operations getObjPositionInParent
        see also https://github.com/plone/plone.app.querystring/issues/22
        """
        key = "plone.app.querystring.field.getObjPositionInParent.operations"
        operation = "plone.app.querystring.operation.int.largerThan"
        registry = self.portal.portal_registry

        # check if operation is used for getObjPositionInParent
        operations = registry.get(key)
        self.assertTrue(operation in operations)
