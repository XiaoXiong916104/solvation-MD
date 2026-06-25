#!/usr/bin/env bash
set -euo pipefail

# Run after production_test or production exists.
# This creates Zn-OTF and Zn-water RDF curves.

prefix="${1:-production_test}"

gmx make_ndx -f "${prefix}.gro" -o rdf_groups.ndx <<'EOF'
r ZN
r BFAF
r SOL & a OW
q
EOF

gmx rdf -f "${prefix}.xtc" -s "${prefix}.tpr" -n rdf_groups.ndx -o rdf_ZN_OTF.xvg <<'EOF'
ZN
BFAF
EOF

gmx rdf -f "${prefix}.xtc" -s "${prefix}.tpr" -n rdf_groups.ndx -o rdf_ZN_waterO.xvg <<'EOF'
ZN
SOL_&_OW
EOF

echo "Wrote rdf_ZN_OTF.xvg and rdf_ZN_waterO.xvg"
