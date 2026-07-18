import 'helpers/common.just'

default:
    @just --list

check:
    @make check

test:
    @make test

smoke: check
    @make smoke
