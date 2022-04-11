#!/bin/bash
rm -f lambda.zip
zip --quiet -r -9 lambda.zip *.py answer-dict
