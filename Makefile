OSM_URL ?= https://download.geofabrik.de/russia/central-fed-district-latest.osm.pbf
MOSCOW_BBOX ?= 35.15,54.25,40.2,56.95

PROFILES := car bicycle foot

.PHONY: linux_all linux_download linux_clip linux_up
.PHONY: win_all win_download win_clip win_up
.PHONY: linux_osrm_car linux_osrm_bicycle linux_osrm_foot
.PHONY: win_osrm_car win_osrm_bicycle win_osrm_foot
.PHONY: linux_osrm_all win_osrm_all
.PHONY: linux_osrm_profile win_osrm_profile
.PHONY: clean


linux_all: linux_download linux_clip linux_osrm_all linux_up

linux_download:
	mkdir -p osrm_arts
	test -f osrm_arts/map.osm.pbf || \
		curl -L -o osrm_arts/map.osm.pbf "$(OSM_URL)"

linux_clip: linux_download
	test -f osrm_arts/moscow-oblast.osm.pbf || \
	docker run --rm \
		-v "$(CURDIR)/osrm_arts:/data" \
		stefda/osmium-tool \
		osmium extract \
		--bbox=$(MOSCOW_BBOX) \
		-o /data/moscow-oblast.osm.pbf \
		/data/map.osm.pbf

linux_osrm_car:
	$(MAKE) linux_osrm_profile PROFILE=car

linux_osrm_bicycle:
	$(MAKE) linux_osrm_profile PROFILE=bicycle

linux_osrm_foot:
	$(MAKE) linux_osrm_profile PROFILE=foot

linux_osrm_all: linux_clip linux_osrm_car linux_osrm_bicycle linux_osrm_foot

linux_osrm_profile:
	mkdir -p osrm/$(PROFILE)

	if test -f osrm/$(PROFILE)/.built; then \
		echo "OSRM $(PROFILE) is already built. Skipping."; \
		exit 0; \
	fi

	cp osrm_arts/moscow-oblast.osm.pbf \
		osrm/$(PROFILE)/map.osm.pbf

	docker run --rm \
		-v "$(CURDIR)/osrm/$(PROFILE):/data" \
		osrm/osrm-backend \
		osrm-extract \
		-p /opt/$(PROFILE).lua \
		/data/map.osm.pbf

	docker run --rm \
		-v "$(CURDIR)/osrm/$(PROFILE):/data" \
		osrm/osrm-backend \
		osrm-partition \
		/data/map.osrm

	docker run --rm \
		-v "$(CURDIR)/osrm/$(PROFILE):/data" \
		osrm/osrm-backend \
		osrm-customize \
		/data/map.osrm

	rm -f osrm/$(PROFILE)/map.osm.pbf

	touch osrm/$(PROFILE)/.built

linux_up:
	docker compose up -d --build


win_all: win_download win_clip win_osrm_all win_up

win_download:
	cmd /C "if not exist osrm_arts mkdir osrm_arts"
	cmd /C "if not exist osrm_arts\map.osm.pbf curl -L -o osrm_arts\map.osm.pbf $(OSM_URL)"

win_clip: win_download
	cmd /C "if not exist osrm_arts\moscow-oblast.osm.pbf docker run --rm -v \"$(CURDIR)/osrm_arts:/data\" stefda/osmium-tool osmium extract --bbox=$(MOSCOW_BBOX) -o /data/moscow-oblast.osm.pbf /data/map.osm.pbf"

win_osrm_car:
	$(MAKE) win_osrm_profile PROFILE=car

win_osrm_bicycle:
	$(MAKE) win_osrm_profile PROFILE=bicycle

win_osrm_foot:
	$(MAKE) win_osrm_profile PROFILE=foot

win_osrm_all: win_clip win_osrm_car win_osrm_bicycle win_osrm_foot

win_osrm_profile:
	cmd /C "if not exist osrm mkdir osrm"
	cmd /C "if not exist osrm\\$(PROFILE) mkdir osrm\\$(PROFILE)"

	cmd /C "if exist osrm\\$(PROFILE)\\.built (echo OSRM $(PROFILE) is already built. Skipping.) else (copy /Y osrm_arts\\moscow-oblast.osm.pbf osrm\\$(PROFILE)\\map.osm.pbf && docker run --rm -v \"$(CURDIR)/osrm/$(PROFILE):/data\" osrm/osrm-backend osrm-extract -p /opt/$(PROFILE).lua /data/map.osm.pbf && docker run --rm -v \"$(CURDIR)/osrm/$(PROFILE):/data\" osrm/osrm-backend osrm-partition /data/map.osrm && docker run --rm -v \"$(CURDIR)/osrm/$(PROFILE):/data\" osrm/osrm-backend osrm-customize /data/map.osrm && del osrm\\$(PROFILE)\\map.osm.pbf && type nul > osrm\\$(PROFILE)\\.built)"

win_up:
	docker compose up -d --build

clean:
	rm -rf osrm_arts
	rm -rf osrm