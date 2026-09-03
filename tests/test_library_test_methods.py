"""Unit tests for Library service Test Methods and Presets."""

from __future__ import annotations

import unittest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.services.library.repository import LibraryRepository, set_library_repository
from backend.services.library.schemas import (
    InputRequirements,
    InstructionalConditions,
    PanelistEligibility,
    PrerequisitesSchema,
    PresetCreate,
    TestMethodCreate,
)


class TestLibraryTestMethods(unittest.TestCase):
    def setUp(self) -> None:
        # Use an isolated in-memory SQLite repository for each test
        self.test_repo = LibraryRepository(db_path=":memory:")
        set_library_repository(self.test_repo)
        self.client = TestClient(app)

    def tearDown(self) -> None:
        self.test_repo.close()
        set_library_repository(None)

    def test_create_and_get_method_with_presets(self) -> None:
        payload = TestMethodCreate(
            name="Triangle Test",
            category="discrimination",
            description="Difference test between two formulations.",
            procedure=["Prepare 3 samples (2 A, 1 B)", "Serve randomized triad", "Identify odd sample"],
            assumptions=["Guessing probability p0 = 1/3", "Independent trials"],
            initial_presets=[
                PresetCreate(
                    name="Standard 30-Panelist",
                    description="Alpha = 0.05 power test",
                    prerequisites=PrerequisitesSchema(
                        input_requirements=InputRequirements(default_panelist_count=30, default_sample_count=3),
                        instructional_conditions=InstructionalConditions(lighting="Red sensory light"),
                        panelist_eligibility=PanelistEligibility(qualification_level="Screened acuity"),
                    ),
                )
            ],
        )

        res = self.client.post("/api/library/methods", json=payload.model_dump())
        self.assertEqual(res.status_code, 201)
        data = res.json()

        method_id = data["id"]
        self.assertEqual(data["name"], "Triangle Test")
        self.assertEqual(data["category"], "discrimination")
        self.assertEqual(data["status"], "draft")
        self.assertEqual(len(data["presets"]), 1)
        self.assertTrue(data["presets"][0]["is_default"])
        self.assertEqual(data["presets"][0]["prerequisites"]["input_requirements"]["default_panelist_count"], 30)

        # GET by ID
        get_res = self.client.get(f"/api/library/methods/{method_id}")
        self.assertEqual(get_res.status_code, 200)
        self.assertEqual(get_res.json()["id"], method_id)

    def test_create_empty_method_and_add_presets_incrementally(self) -> None:
        create_res = self.client.post(
            "/api/library/methods",
            json={
                "name": "QDA Descriptive",
                "category": "descriptive",
                "description": "Sensory profiling",
                "procedure": ["Train panel", "Evaluate intensity"],
                "assumptions": ["Scale linearity"],
                "initial_presets": [],
            },
        )
        self.assertEqual(create_res.status_code, 201)
        method_id = create_res.json()["id"]
        self.assertEqual(len(create_res.json()["presets"]), 0)

        # Add preset 1 (should automatically become default)
        p1_res = self.client.post(
            f"/api/library/methods/{method_id}/presets",
            json={
                "name": "12-Judge Trained Panel",
                "description": "3 replicates",
                "prerequisites": {
                    "input_requirements": {"default_panelist_count": 12},
                    "instructional_conditions": {},
                    "panelist_eligibility": {"qualification_level": "Trained descriptive judge"},
                },
                "output_schema": {"primary_metric": "ANOVA F-test", "metrics": ["sample_f", "panelist_f"]},
                "is_default": False,
            },
        )
        self.assertEqual(p1_res.status_code, 201)
        p1_data = p1_res.json()
        self.assertTrue(p1_data["is_default"])

        # Add preset 2 as explicit default (should demote preset 1)
        p2_res = self.client.post(
            f"/api/library/methods/{method_id}/presets",
            json={
                "name": "8-Judge Rapid Screening",
                "prerequisites": {},
                "output_schema": {},
                "is_default": True,
            },
        )
        self.assertEqual(p2_res.status_code, 201)
        self.assertTrue(p2_res.json()["is_default"])

        # Verify method has 2 presets, with preset 2 as default
        method_detail = self.client.get(f"/api/library/methods/{method_id}").json()
        self.assertEqual(len(method_detail["presets"]), 2)
        defaults = [p for p in method_detail["presets"] if p["is_default"]]
        self.assertEqual(len(defaults), 1)
        self.assertEqual(defaults[0]["name"], "8-Judge Rapid Screening")

    def test_list_and_filter_methods(self) -> None:
        self.client.post(
            "/api/library/methods",
            json={"name": "Triangle Test", "category": "discrimination", "procedure": [], "assumptions": []},
        )
        self.client.post(
            "/api/library/methods",
            json={"name": "Duo-Trio Test", "category": "discrimination", "procedure": [], "assumptions": []},
        )
        self.client.post(
            "/api/library/methods",
            json={"name": "9-Point Hedonic", "category": "hedonic", "procedure": [], "assumptions": []},
        )

        # Filter by category
        res_disc = self.client.get("/api/library/methods?category=discrimination")
        self.assertEqual(len(res_disc.json()), 2)

        res_hed = self.client.get("/api/library/methods?category=hedonic")
        self.assertEqual(len(res_hed.json()), 1)
        self.assertEqual(res_hed.json()[0]["name"], "9-Point Hedonic")

        # Search term
        res_search = self.client.get("/api/library/methods?search=Triangle")
        self.assertEqual(len(res_search.json()), 1)
        self.assertEqual(res_search.json()[0]["name"], "Triangle Test")

    def test_duplication_flow(self) -> None:
        create_res = self.client.post(
            "/api/library/methods",
            json={
                "name": "Standard Triangle",
                "category": "discrimination",
                "description": "Original",
                "procedure": ["Step 1"],
                "assumptions": ["Assumption 1"],
                "initial_presets": [{"name": "Preset 1", "prerequisites": {}, "output_schema": {}, "is_default": True}],
            },
        )
        source_id = create_res.json()["id"]

        dup_res = self.client.post(
            f"/api/library/methods/{source_id}/duplicate",
            json={"new_name": "Custom Modified Triangle"},
        )
        self.assertEqual(dup_res.status_code, 201)
        dup_data = dup_res.json()

        self.assertNotEqual(dup_data["id"], source_id)
        self.assertEqual(dup_data["name"], "Custom Modified Triangle")
        self.assertEqual(dup_data["derived_from_id"], source_id)
        self.assertEqual(dup_data["status"], "draft")
        self.assertEqual(len(dup_data["presets"]), 1)
        self.assertEqual(dup_data["presets"][0]["name"], "Preset 1")
        self.assertNotEqual(dup_data["presets"][0]["id"], create_res.json()["presets"][0]["id"])

    def test_immutability_and_usage_guards(self) -> None:
        create_res = self.client.post(
            "/api/library/methods",
            json={
                "name": "Sensory Profile",
                "category": "descriptive",
                "procedure": [],
                "assumptions": [],
                "initial_presets": [{"name": "Standard Setup", "prerequisites": {}, "output_schema": {}}],
            },
        )
        method_id = create_res.json()["id"]
        preset_id = create_res.json()["presets"][0]["id"]

        # Simulate usage in a Lab session
        self.test_repo.increment_preset_usage(preset_id)

        # Verify status is now active
        updated_method = self.client.get(f"/api/library/methods/{method_id}").json()
        self.assertEqual(updated_method["status"], "active")
        self.assertEqual(updated_method["total_usage_count"], 1)

        # Attempt to edit locked preset -> should fail (400)
        edit_preset_res = self.client.put(
            f"/api/library/presets/{preset_id}",
            json={"name": "Altered Name"},
        )
        self.assertEqual(edit_preset_res.status_code, 400)

        # Attempt to delete locked preset -> should fail (400)
        del_preset_res = self.client.delete(f"/api/library/presets/{preset_id}")
        self.assertEqual(del_preset_res.status_code, 400)

        # Attempt to change method category -> should fail (400)
        edit_method_res = self.client.put(
            f"/api/library/methods/{method_id}",
            json={"category": "hedonic"},
        )
        self.assertEqual(edit_method_res.status_code, 400)

        # Attempt to delete used method -> should fail (400)
        del_method_res = self.client.delete(f"/api/library/methods/{method_id}")
        self.assertEqual(del_method_res.status_code, 400)

        # Adding a NEW preset to the used method -> should SUCCEED!
        new_p_res = self.client.post(
            f"/api/library/methods/{method_id}/presets",
            json={"name": "New Variation Preset", "prerequisites": {}, "output_schema": {}},
        )
        self.assertEqual(new_p_res.status_code, 201)

    def test_archival_and_draft_deletion(self) -> None:
        # Draft deletion test
        m1 = self.client.post(
            "/api/library/methods",
            json={"name": "Draft Mistake", "category": "hedonic", "procedure": [], "assumptions": []},
        ).json()
        del_res = self.client.delete(f"/api/library/methods/{m1['id']}")
        self.assertEqual(del_res.status_code, 200)

        get_res = self.client.get(f"/api/library/methods/{m1['id']}")
        self.assertEqual(get_res.status_code, 404)

        # Archival test
        m2 = self.client.post(
            "/api/library/methods",
            json={
                "name": "Method to Archive",
                "category": "hedonic",
                "procedure": [],
                "assumptions": [],
                "initial_presets": [{"name": "P1", "prerequisites": {}, "output_schema": {}}],
            },
        ).json()
        archive_res = self.client.post(f"/api/library/methods/{m2['id']}/archive")
        self.assertEqual(archive_res.status_code, 200)
        archived_data = archive_res.json()
        self.assertEqual(archived_data["status"], "archived")
        self.assertEqual(archived_data["presets"][0]["status"], "archived")


if __name__ == "__main__":
    unittest.main()
