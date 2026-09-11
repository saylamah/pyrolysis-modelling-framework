# Release Status

**Prepared release:** `v0.2.0`  
**State:** RELEASE-READY / DOI RESERVED / NOT YET ARCHIVED  
**Earliest authorized publication date:** `2026-10-01`  
**Frozen scientific baseline:** tag `v0.1.1`, commit `4786892b262e89ba576b1eca868704bf28b3e22a`  
**Prepublication integration baseline:** `main` commit `d3774a15fc422f028d9a325b64560c85465fcaca`  
**Controlled tested code/science lock before final rights/status metadata synchronization:** `aaba4f503f77e6d44833111c77661c9baa515a61`  
**Hosted release-gate CI for that lock:** run `34598677977` — PASS  
**Previous published version DOI:** `10.5281/zenodo.22143183`  
**Concept DOI:** `10.5281/zenodo.22129133`  
**Reserved v0.2.0 version DOI:** `10.5281/zenodo.22707516` — Zenodo new-version draft; not registered/live until publication

Version `v0.2.0` preserves the qualified v0.1.1 SFOR scientific baseline and adds the rights-safe extension layer documented in `RELEASE_NOTES_v0.2.0.md`. The four commits between the v0.1.1 tag and the prepublication integration baseline were post-release metadata synchronization for v0.1.1; the v0.2.0 branch was then integrated and tested from that current `main` state.

The release must not be tagged or published before 2026-10-01. Commit `aaba4f503f77e6d44833111c77661c9baa515a61` passed the complete hosted release gate, including Ubuntu/Python 3.10, Ubuntu/Python 3.13, Windows/Python 3.13, the v0.2.0 release-integrity guard, unit tests, qualified-example checks, deterministic example-suite verification, wheel build/inspection and clean-wheel installation where configured.

The reserved DOI is intentionally embedded in citation/release metadata before publication so the exact archived artifact can carry its final identifier. Reservation does not make the DOI a published or experimentally validated object.

The rights/status metadata synchronization following the tested code/science lock changes no kinetic equation, parameter, numerical result, evidence classification, dependency or executable model behaviour. Because it creates a new branch head, that head must also pass the complete hosted release gate before it can be used for the final tag.

If any code, scientific value, evidence class, dependency, rights/provenance statement or release metadata changes after the final tested branch head is established, the complete release gate must be rerun before publication.

On or after 2026-10-01, if the controlled branch head remains unchanged and the final release gate passes, create tag `v0.2.0`, publish the GitHub release, upload/archive that exact tagged release in the existing Zenodo software concept/version chain using the reserved DOI draft, and publish the Zenodo software record. Only after DOI `10.5281/zenodo.22707516` resolves as the live v0.2.0 record should the manuscript, Supplementary Information and outward-facing platform metadata be synchronized to the verified software release.

This release state does not close the broader DP-06 Pyrolysis Modelling Framework programme.
