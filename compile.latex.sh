#!/bin/bash

tex_file=$1

echo "> Compiling ${tex_file}"

latex --shell-escape ${tex_file}

pdflatex --shell-escape ${tex_file}

echo "> Compilation done !"
