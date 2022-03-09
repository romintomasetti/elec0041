#!/bin/bash

set -ex

COMMON_OPTIONS="-halt-on-error"

tex_file=$1

echo "> Compiling ${tex_file}"

latex    --shell-escape ${COMMON_OPTIONS} ${tex_file}

pdflatex --shell-escape ${COMMON_OPTIONS} ${tex_file}

echo "> Compilation done !"
