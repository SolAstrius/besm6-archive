#!/bin/sh
# SPDX-License-Identifier: Apache-2.0
# Download the БЭСМ-6 volume images published by the besm6 project into disks/ and verify them.
# Volume numbers (dispak names): sbor2048=2048 sbor2053=2053 svs2048=2148 svs2053=2153 svs2113=2113
# alt2048=2248 krab2063=2063 krab2086=2086 tape1=4001 tape23=4023.
set -eu
cd "$(dirname "$0")/.."
mkdir -p disks
URL=https://github.com/besm6/besm6.github.io/raw/HEAD/download/disks
while read -r sum name; do
    [ -s "disks/$name" ] || curl -sfL -o "disks/$name" "$URL/$name"
    echo "$sum  disks/$name"
done <<'LIST' | shasum -a 256 -c -
45ecfa45bb6d75829ec0690c6b47994aabbb238778a6714375044dab8c220a80 alt2048.bin
e3bb28e4bb816eefac2b2513758d843c05ef6bd4b66e447f11e637c7c7d3f6fc krab2063.bin
1fe3bc4159b151153f3f0b6a2a006af459f26a02769b365457a160f9e988622c krab2086.bin
844919c089de8afad8f2adbf428a2013f780b2679f377e9506f834d03433dc51 sbor2048.bin
a9bdbbdd0f0eaf517fd09c86b30ad1917c41c06f9986cb9d50c3704fd9c60342 sbor2053.bin
75617c04fee7d90dfce12d7ea82fe8c5ae88897825508094313f970ace59b69b svs2048.bin
2ede95db996cc8dc43e81e2ff633beb2038c16a811459f6368de6b78007fdadd svs2053.bin
c631e8d8e340441f593aa2e5028e8157158077b2732eabbc4e11be75939100bb svs2113.bin
30223751b839a6273cf96a0a6ab2e8becfcef2a59dd16661022b39740974b978 tape1.bin
71ea1c3aac2d2c9aa85d69ba1328a17ccd38d59860d11b96fa7d726be1d875c5 tape23.bin
LIST
mkdir -p volumes
for pair in sbor2048:2048 sbor2053:2053 svs2048:2148 svs2053:2153 svs2113:2113 alt2048:2248 \
            krab2063:2063 krab2086:2086 tape1:4001 tape23:4023; do
    ln -sf "../disks/${pair%%:*}.bin" "volumes/${pair##*:}"
done
