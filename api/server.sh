#!/bin/bash -v

MARIAN=./tools/marian-dev/build

if [ $# -lt 3 ]; then
    echo "usage: $0 <model-dir> <input-file> <output-file> <marian-options>" 1>&2
    exit 1
fi

if [ ! -e $MARIAN/marian-decoder ]; then
    echo "marian-decoder is not compiled in $MARIAN/" 1>&2
    exit 1
fi

MODEL=$1
shift
# The input needs to be tokenizer with the spaCy tokenizer
INPUT=$1
shift
OUTPUT=$1
shift


# Generate the n-best list with the ensemble NMT + LM system
$MARIAN/marian-server --port 8080 -c $MODEL/config.yml --n-best -i $INPUT -o $OUTPUT.nbest0 --log $OUTPUT.server.log $@
