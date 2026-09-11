# Release Status

**Prepared release:** `v0.2.0`  
**State:** RELEASE-READY / NOT YET ARCHIVED  
**Earliest authorized publication date:** `2026-10-01`  
**Frozen scientific baseline:** tag `v0.1.1`, commit `4786892b262e89ba576b1eca868704bf28b3e22a`  
**Prepublication integration baseline:** `main` commit `d3774a15fc422f028d9a325b64560c85465fcaca`  
**Previously tested prepublication head:** `305cc64e3b9a8845a5ada795582975c579ed798e`  
**Previously completed hosted release-gate CI:** run `34586928266` — PASS  
**Previous published version DOI:** `10.5281/zenodo.22143183`  
**Concept DOI:** `10.5281/zenodo.22129133`  
**v0.2.0 version DOI:** not assigned before archival

Version `v0.2.0` preserves the qualified v0.1.1 SFOR scientific baseline and adds the rights-safe extension layer documented in `RELEASE_NOTES_v0.2.0.md`. The four commits between the v0.1.1 tag and the prepublication integration baseline were post-release metadata synchronization for v0.1.1; the v0.2.0 branch was then integrated and tested from that current `main` state.

The release must not be tagged or published before 2026-10-01. The prepublication source state identified above passed the complete hosted release gate, including Ubuntu/Python 3.10, Ubuntu/Python 3.13, Windows/Python 3.13, wheel build/inspection and clean-wheel installation. This status-document update creates a new branch head and therefore requires the hosted release gate to pass again before that new head can become the controlled tested source lock.

If any code, scientific value, evidence class, dependency, rights/provenance statement or release metadata changes after the newly tested source lock, the complete release gate must be rerun and the new tested commit recorded before publication.

On or after 2026-10-01, if the tested source remains unchanged and the final release gate passes, create tag `v0.2.0`, publish the GitHub release, and archive that exact tag in the existing Zenodo software concept record. Only after the Zenodo version DOI is verified should the live repository metadata, manuscript and Supplementary Information be synchronized to that DOI.

This release state does not close the broader DP-06 Pyrolysis Modelling Framework programme.
