# Pending Repository Updates

Items discussed in conversation that need to be applied to the repo.
Work through these in a dedicated session.

---

## hardware-spec.md

- [ ] Add enclosure materials section — PETG body, Shore 95A TPU gasket, design notes
      (discussed: compression lid, stainless hardware, drip edge, gland placement,
      wall thickness 3-4 perimeters, 40%+ infill, louvered vent as separate insert)

- [ ] Update power section — replace IRM-30-5 GPIO path with USB-C supply via
      female spade terminals on plug prongs, connected to hot/neutral in junction box,
      USB-C cable through IP68 gland into enclosure to Pi 5 USB-C port

- [ ] Add wiring diagram document to /docs covering full power chain:
      Outlet → GFCI → junction box → spade terminals on USB-C supply plug →
      USB-C cable → IP68 gland → Pi 5 USB-C port

- [ ] Add network section — Pi 5 built-in Wi-Fi (no Ethernet run available);
      note on metal enclosure attenuation risk; static IP / DHCP reservation recommended

---

## README.md

- [ ] Update shopping list to reflect USB-C power supply instead of IRM + GPIO path
- [ ] Add enclosure section linking to /enclosure directory

---

## New Files Needed

- [ ] /docs/wiring-diagram.md — full power chain documentation
- [ ] /docs/enclosure-design-notes.md — PETG/TPU material choices, CAD design guidelines,
      thermal separation, fan cutout dimensions (40mm, 32mm bolt circle),
      gland placement rules, compression lid spec
- [ ] /scripts/auto_delete.py — cron-based retention policy script:
      /clips/ 7 days, /snapshots/ 30 days, /saved/ never touched
- [ ] /scripts/mount_nas.sh — NFS mount script (pending NAS build)
- [ ] /config/.env.example — environment variable template

---

## camera/identify.py + database/db.py

- [ ] Only generate Cornell Lab links when iNaturalist result is a bird
      (check `iconic_taxon_name == "Aves"` in API response before building URLs)
- [ ] Fix eBird URL format — eBird uses 6-letter species codes (e.g. `houfin`)
      not common name slugs. Look up correct code via eBird API or iNaturalist
      taxon data
- [ ] Update `min_confidence` threshold in identify.py to use a meaningful
      cutoff on the raw score (suggest 50) rather than 0.10 which is ineffective
- [ ] Add Samba file share setup to /docs or /scripts for PC access to captures
      and database

---

## camera/bird_capture.py

- [ ] Update SAVE_DIR to NAS NFS mount path once NAS is built
      (current: /home/steve/birdfeeder/captures)
- [ ] Update script path in bird_capture.service to match final deployment location
