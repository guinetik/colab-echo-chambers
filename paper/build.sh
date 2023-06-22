#!/bin/bash
###################################################################
# Script Name   : build.sh
# Description   : Generates the paper in PDF format. Runs pdflatex, bibtex, makeglossaries, and makeindex.
# Args          : -
# Author        : João Guilherme
# Email         : guinetik@gmail.com
###################################################################

# Color variables
CYAN="\033[0;36m"
NC='\033[0m'     # No Color
BOLD=$(tput bold)
NORM=$(tput sgr0)

set -T
# Traps logging-like commands specified by the NOTRACE flag
trap '! [[ "$BASH_COMMAND" =~ ^(status|log_step|draw_line|NOTRACE=) ]] && printf "+ %s\n" "$BASH_COMMAND"' DEBUG

# Prints a message with formatting
# Usage: status <message>
status() {
    NOTRACE=1 echo -e "$@"
}

# Draws a line separator
# Usage: draw_line
draw_line() {
    NOTRACE=1 echo -e "------------------------------------------------------------"
}

# Logs a step message with formatting and draws a line separator
# Usage: log_step <step_message>
log_step() {
    draw_line
    status "${CYAN}${BOLD} $@ ${NC}${NORM}"
}

# Runs pdflatex in silent mode for initial build without generating PDF
# Usage: silent_build
silent_build() {
    NOTRACE=1 pdflatex -draftmode -interaction=batchmode -halt-on-error -output-directory out main.tex | grep '^!.*' -A200 --color=always
}

# Cleans up the output directory
cleanup() {
    log_step "Cleaning up"
    rm -rf ./out
    mkdir out
}

# Generates metadata and performs initial build
generate_metadata() {
    log_step "Generating metadata"
    silent_build
}

# Generates bibliography
generate_bibliography() {
    log_step "Generating bibliography"
    bibtex out/main
}

# Generates glossary
generate_glossary() {
    log_step "Generating glossary"
    makeglossaries -d out main
}

# Generates nomenclature
generate_nomenclature() {
    log_step "Generating nomenclature"
    makeindex out/main.nlo -s nomencl.ist -o out/main.nls
}

# Regenerates metadata and performs final build to generate PDF
regenerate_metadata_and_build_pdf() {
    log_step "Regenerating Metadata"
    silent_build

    log_step "Generating PDF"
    pdflatex -halt-on-error -output-directory out main.tex
}

# Main script execution
NOTRACE=1 cleanup
NOTRACE=1 generate_metadata
NOTRACE=1 generate_bibliography
NOTRACE=1 generate_glossary
NOTRACE=1 generate_nomenclature
NOTRACE=1 regenerate_metadata_and_build_pdf