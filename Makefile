# QtMesh Validation Demo — local marketing / QA targets
QTMESH ?= qtmesh
REPORTS := reports

.PHONY: help assets demos scan good issues profiles fix cloud character roblox clean-reports

help:
	@echo "QtMesh Validation Demo"
	@echo "  make assets      Regenerate demo meshes (needs Blender)"
	@echo "  make demos       Run all marketing validation demos"
	@echo "  make scan        Full mobile campaign scan"
	@echo "  make good        Scan only green assets"
	@echo "  make issues      Scan intentional problem assets"
	@echo "  make roblox      Roblox MeshPart (20k) vs accessory (4k) demos"
	@echo "  make profiles    Compare platform profiles on one overbudget mesh"
	@echo "  make fix         Before/after fix pipeline demo"
	@echo "  make cloud       Local or Cloud-upload scan"
	@echo "  make character   Print / gate character pipeline"
	@echo "  make docker      Scan via ghcr.io/fernandotonon/qtmesh"

assets:
	blender --background --python scripts/generate_demo_assets.py

demos:
	bash scripts/run_all_demos.sh

scan:
	mkdir -p $(REPORTS)
	$(QTMESH) scan --config configs/mobile-campaign.yml --report $(REPORTS)/mobile-campaign.json --sarif $(REPORTS)/mobile-campaign.sarif --no-upload || true

good:
	mkdir -p $(REPORTS)
	$(QTMESH) scan --config configs/good-only.yml --report $(REPORTS)/good-only.json --no-upload

issues:
	mkdir -p $(REPORTS)
	$(QTMESH) scan assets/issues --config configs/mobile-campaign.yml --report $(REPORTS)/issues-only.json --no-upload || true

profiles:
	bash scripts/demo_profiles.sh

fix:
	bash scripts/demo_fix_pipeline.sh

cloud:
	bash scripts/demo_cloud.sh

character:
	bash scripts/demo_character_pipeline.sh

roblox:
	bash scripts/demo_roblox.sh

docker:
	bash pipelines/docker-scan.sh

clean-reports:
	rm -rf $(REPORTS)/*
